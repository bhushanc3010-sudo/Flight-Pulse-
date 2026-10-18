
import logging

from config.settings import LOG_DIR
from src.acquisition.flight_api import fetch_live_flights


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                LOG_DIR / "acquisition.log",
                encoding="utf-8",
            ),
        ],
        force=True,
    )

    # One airport and one API request for this first run.
    result = fetch_live_flights(
        airport="BOM",
        limit=10,
        direction="departure",
    )

    print("\nFlight Pulse - Acquisition Result")
    print("---------------------------------")
    print("Airport:", result["airport"])
    print("Direction:", result["direction"])
    print("Records saved:", result["record_count"])
    print("Provider-reported total:", result["provider_total"])
    print("Raw file:", result["raw_file"])


if __name__ == "__main__":
    main()
