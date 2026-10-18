
from src.cleaning.clean_flights import clean_flights
from src.cleaning.quality_checks import generate_quality_report


def main():
    df, cleaning_metrics = clean_flights()

    report = generate_quality_report(
        df,
        extra_metrics=cleaning_metrics,
    )

    print("\nModule 2 completed.")
    print("Output: data/processed/flights_cleaned.csv")
    print("Output: data/processed/quality_report.json")

    if report["total_records"] == 0:
        print("WARNING: No flight records are available.")


if __name__ == "__main__":
    main()
