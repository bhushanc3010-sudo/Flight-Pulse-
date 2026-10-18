
import hashlib
import json

import pandas as pd
from supabase import create_client

from config.settings import (
    PROCESSED_DIR,
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


CSV_FILE = PROCESSED_DIR / "flights_cleaned.csv"
TABLE_NAME = "flight_observations"


def to_json_safe(value):
    """Convert pandas values into JSON/PostgreSQL-friendly values."""
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    return value


def make_record_key(row):
    """Create a deterministic key for repeatable imports."""
    canonical = json.dumps(
        row,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def main():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise SystemExit("Supabase credentials are missing in .env")

    if not CSV_FILE.exists():
        raise SystemExit(
            f"Cleaned CSV not found: {CSV_FILE}. "
            "Run Module 2 first."
        )

    df = pd.read_csv(CSV_FILE)

    if df.empty:
        print("Cleaned CSV contains no records. Nothing to load.")
        return

    # Convert NaN, NaT and pandas-specific types before uploading.
    rows = [
        {
            column: to_json_safe(value)
            for column, value in row.items()
        }
        for row in df.to_dict(orient="records")
    ]

    # Add deterministic keys so rerunning the loader is idempotent.
    for row in rows:
        row["record_key"] = make_record_key(row)

    client = create_client(
        SUPABASE_URL,
        SUPABASE_SECRET_KEY,
    )

    batch_size = 100
    uploaded = 0

    for start in range(0, len(rows), batch_size):
        batch = rows[start:start + batch_size]

        client.table(TABLE_NAME).upsert(
            batch,
            on_conflict="record_key",
        ).execute()

        uploaded += len(batch)
        print(f"Processed {uploaded}/{len(rows)} records")

    print("\nFlight Pulse database load completed.")
    print("CSV rows processed:", len(rows))
    print("Table:", TABLE_NAME)
    print("Mode: upsert (safe to rerun for identical records)")


if __name__ == "__main__":
    main()
