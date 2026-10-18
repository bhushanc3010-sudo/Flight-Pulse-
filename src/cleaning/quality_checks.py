
import json

from config.settings import PROCESSED_DIR


def generate_quality_report(df, extra_metrics=None):
    """Generate and save a JSON data-quality report."""

    required_columns = [
        "snapshot_id",
        "flight_number",
        "departure_iata",
        "arrival_iata",
        "scheduled_departure_utc",
        "actual_departure_utc",
        "departure_delay_minutes",
        "delay_status",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns missing: {missing_columns}"
        )

    duplicate_keys = [
        "snapshot_id",
        "flight_number",
        "departure_iata",
        "arrival_iata",
        "scheduled_departure_utc",
    ]

    # Ignore incomplete identities when counting duplicates.
    complete_identity = df[duplicate_keys].notna().all(axis=1)

    duplicate_mask = (
        complete_identity
        & df.duplicated(
            subset=duplicate_keys,
            keep=False,
        )
    )

    delay_values = df["departure_delay_minutes"]

    report = {
        "total_records": int(len(df)),
        "unique_snapshots": int(df["snapshot_id"].nunique()),
        "missing_values_by_column": {
            column: int(count)
            for column, count in df.isna().sum().items()
        },
        "delay_status_counts": {
            str(status): int(count)
            for status, count in df["delay_status"]
            .value_counts(dropna=False)
            .items()
        },
        "records_missing_flight_number": int(
            df["flight_number"].isna().sum()
        ),
        "records_missing_scheduled_departure": int(
            df["scheduled_departure_utc"].isna().sum()
        ),
        "records_missing_actual_departure": int(
            df["actual_departure_utc"].isna().sum()
        ),
        "records_with_calculated_delay": int(
            delay_values.notna().sum()
        ),
        "negative_delay_values": int(
            (delay_values.dropna() < 0).sum()
        ),
        "same_snapshot_duplicate_rows": int(
            duplicate_mask.sum()
        ),
    }

    if extra_metrics:
        report.update(extra_metrics)

    output_file = PROCESSED_DIR / "quality_report.json"

    output_file.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nData Quality Report")
    print("-------------------")
    print("Total records:", report["total_records"])
    print("Unique snapshots:", report["unique_snapshots"])
    print(
        "Missing actual departure:",
        report["records_missing_actual_departure"],
    )
    print(
        "Records with calculated delay:",
        report["records_with_calculated_delay"],
    )
    print(
        "Same-snapshot duplicate rows:",
        report["same_snapshot_duplicate_rows"],
    )
    print("Report saved to:", output_file)

    return report
