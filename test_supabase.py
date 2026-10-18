
from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_SECRET_KEY


def main():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise SystemExit(
            "Missing SUPABASE_URL or SUPABASE_SECRET_KEY in .env"
        )

    client = create_client(
        SUPABASE_URL,
        SUPABASE_SECRET_KEY,
    )

    response = (
        client.table("flight_observations")
        .select("record_key")
        .limit(1)
        .execute()
    )

    print("Supabase connection successful.")
    print("Table is accessible.")
    print("Sample rows returned:", len(response.data))


if __name__ == "__main__":
    main()
