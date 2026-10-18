
import json
from config.settings import RAW_DIR, PROCESSED_DIR


import pandas as pd


def get_nested(record, *keys):
    """Safely retrieve a nested value from a dictionary."""
    value = record

    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)

    return value


def clean_flights():
    raw_files = sorted(RAW_DIR.glob("*.json"))

    if not raw_files:
        raise FileNotFoundError(
            f"No raw JSON files found in {RAW_DIR}"
        )

    rows = []

    for raw_file in raw_files:
        try:
            with raw_file.open("r", encoding="utf-8") as file:
                document = json.load(file)
        except (json.JSONDecodeError, OSError) as exc:
            print(
                f"Skipping unreadable file: {raw_file.name} "
                f"({type(exc).__name__})"
            )
            continue

        metadata = document.get("ingestion_metadata", {})
        api_response = document.get("api_response", {})

        if not isinstance(metadata, dict):
            metadata = {}

        if not isinstance(api_response, dict):
            print(f"Skipping invalid response: {raw_file.name}")
            continue

        records = api_response.get("data", [])

        if not isinstance(records, list):
            print(f"Skipping invalid data list: {raw_file.name}")
            continue

        snapshot_time = metadata.get("retrieved_at_utc")
        snapshot_id = snapshot_time or raw_file.stem

        for record in records:
            if not isinstance(record, dict):
                continue

            scheduled = get_nested(
                record, "departure", "scheduled"
            )
            actual = get_nested(
                record, "departure", "actual"
            )

            rows.append({
                "snapshot_id": snapshot_id,
                "snapshot_time_utc": snapshot_time,
                "flight_date": (
                    record.get("flight_date")
                    or get_nested(record, "flight", "date")
                ),
                "flight_number": get_nested(
                    record, "flight", "iata"
                ),
                "airline": get_nested(
                    record, "airline", "name"
                ),
                "flight_status": record.get("flight_status"),
                "departure_iata": get_nested(
                    record, "departure", "iata"
                ),
                "arrival_iata": get_nested(
                    record, "arrival", "iata"
                ),
                "scheduled_departure_utc": scheduled,
                "actual_departure_utc": actual,
                "data_source": "Aviationstack",
            })

    if not rows:
        raise ValueError(
            "No valid flight records found in the raw JSON files."
        )

    df = pd.DataFrame(rows)

    # Standardize text values.
    text_columns = [
        "flight_number",
        "airline",
        "flight_status",
        "departure_iata",
        "arrival_iata",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # Normalize identifiers and airport codes.
    for column in [
        "flight_number",
        "departure_iata",
        "arrival_iata",
    ]:
        df[column] = df[column].str.upper()

    # Parse timestamps in UTC.
    timestamp_columns = [
        "snapshot_time_utc",
        "scheduled_departure_utc",
        "actual_departure_utc",
    ]

    for column in timestamp_columns:
        df[column] = pd.to_datetime(
            df[column],
            utc=True,
            errors="coerce",
        )

    # Derive flight date from scheduled departure if needed.
    parsed_flight_date = pd.to_datetime(
        df["flight_date"],
        errors="coerce",
        utc=True,
    )

    scheduled_date = (
        df["scheduled_departure_utc"]
        .dt.strftime("%Y-%m-%d")
    )

    df["flight_date"] = (
        parsed_flight_date.dt.strftime("%Y-%m-%d")
        .fillna(scheduled_date)
    )

    # Calculate delay only when both timestamps are available.
    calculable = (
        df["actual_departure_utc"].notna()
        & df["scheduled_departure_utc"].notna()
    )

    difference = (
        df["actual_departure_utc"]
        - df["scheduled_departure_utc"]
    ).dt.total_seconds() / 60

    df["departure_delay_minutes"] = float("nan")

    # Negative differences represent early departures.
    # For reporting, early/on-time departures have zero delay.
    df.loc[calculable, "departure_delay_minutes"] = (
        difference.loc[calculable].clip(lower=0).round()
    )

    df["delay_status"] = "Unknown"

    df.loc[
        calculable & (difference < 15),
        "delay_status",
    ] = "Not delayed"

    df.loc[
        calculable & (difference >= 15),
        "delay_status",
    ] = "Delayed"

    # Deduplicate only within the same snapshot, and only
    # where all identity fields are present.
    duplicate_keys = [
        "snapshot_id",
        "flight_number",
        "departure_iata",
        "arrival_iata",
        "scheduled_departure_utc",
    ]

    complete_identity = df[duplicate_keys].notna().all(axis=1)

    duplicate_mask = pd.Series(False, index=df.index)

    duplicate_mask.loc[complete_identity] = (
        df.loc[complete_identity]
        .duplicated(subset=duplicate_keys, keep="first")
    )

    duplicates_removed = int(duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()

    columns = [
        "snapshot_id",
        "snapshot_time_utc",
        "flight_date",
        "flight_number",
        "airline",
        "flight_status",
        "departure_iata",
        "arrival_iata",
        "scheduled_departure_utc",
        "actual_departure_utc",
        "departure_delay_minutes",
        "delay_status",
        "data_source",
    ]

    df = df[columns]

    output_file = PROCESSED_DIR / "flights_cleaned.csv"
    df.to_csv(output_file, index=False)

    print(f"Raw files found: {len(raw_files)}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"Cleaned records: {len(df)}")
    print(f"Saved cleaned data to: {output_file}")

    return df, {
        "raw_files_found": len(raw_files),
        "duplicate_rows_removed": duplicates_removed,
    }


if __name__ == "__main__":
    clean_flights()
