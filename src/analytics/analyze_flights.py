
import json
import logging
import math

import pandas as pd

from config.settings import PROCESSED_DIR

INPUT_FILE = PROCESSED_DIR / "flights_cleaned.csv"

OUTPUT_FILES = {
    "airline": PROCESSED_DIR / "airline_performance.csv",
    "airport": PROCESSED_DIR / "airport_performance.csv",
    "route": PROCESSED_DIR / "route_performance.csv",
    "summary": PROCESSED_DIR / "analytics_summary.json",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)


def calculate_metrics(data, group_columns=None):
    """Calculate observation counts and known-delay metrics."""

    df = data.copy()

    # Treat only explicitly classified delays as known outcomes.
    df["is_known_delay"] = df["delay_status"].isin(
        ["Delayed", "Not delayed"]
    )
    df["is_delayed"] = df["delay_status"].eq("Delayed")

    if group_columns:
        result = (
            df.groupby(group_columns, dropna=False)
            .agg(
                observations=("delay_status", "size"),
                known_delay_records=("is_known_delay", "sum"),
                delayed_records=("is_delayed", "sum"),
                average_delay_minutes=(
                    "departure_delay_minutes", "mean"
                ),
            )
            .reset_index()
        )
    else:
        result = pd.DataFrame(
            [
                {
                    "observations": len(df),
                    "known_delay_records": int(
                        df["is_known_delay"].sum()
                    ),
                    "delayed_records": int(
                        df["is_delayed"].sum()
                    ),
                    "average_delay_minutes": df[
                        "departure_delay_minutes"
                    ].mean(),
                }
            ]
        )

    # Avoid division by zero when no delay outcomes are known.
    denominator = result["known_delay_records"].replace(
        0, float("nan")
    )

    result["delayed_rate_percent"] = (
        result["delayed_records"]
        .div(denominator)
        .mul(100)
        .round(2)
    )

    result["average_delay_minutes"] = result[
        "average_delay_minutes"
    ].round(2)

    return result


def make_json_safe(value):
    """Convert pandas/numpy values and NaN to valid JSON values."""

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def main():
    # 1. Load and validate input data.
    if not INPUT_FILE.exists():
        raise SystemExit(
            f"Cleaned data not found: {INPUT_FILE}. "
            "Run the pipeline first."
        )

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise SystemExit("The cleaned flight dataset is empty.")

    required_columns = [
        "airline",
        "departure_iata",
        "arrival_iata",
        "departure_delay_minutes",
        "delay_status",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise SystemExit(
            f"Missing required columns: {missing_columns}. "
            f"Available columns: {df.columns.tolist()}"
        )

    df["departure_delay_minutes"] = pd.to_numeric(
        df["departure_delay_minutes"],
        errors="coerce",
    )

    # 2. Calculate overall dataset metrics.
    summary = calculate_metrics(df).iloc[0].to_dict()

    # Convert summary values to JSON-compatible Python values.
    summary = {
        key: make_json_safe(value)
        for key, value in summary.items()
    }

    summary["total_observations"] = int(len(df))
    summary["unique_airlines"] = int(df["airline"].nunique())
    summary["unique_departure_airports"] = int(
        df["departure_iata"].nunique()
    )
    summary["unique_routes"] = int(
        df[["departure_iata", "arrival_iata"]]
        .dropna()
        .drop_duplicates()
        .shape[0]
    )

    # 3. Analyze airline performance.
    airline = calculate_metrics(df, ["airline"])
    airline = airline.sort_values(
        "observations",
        ascending=False,
    )
    airline.to_csv(OUTPUT_FILES["airline"], index=False)

    # 4. Analyze departure airport performance.
    airport = calculate_metrics(df, ["departure_iata"])
    airport = airport.sort_values(
        "observations",
        ascending=False,
    )
    airport.to_csv(OUTPUT_FILES["airport"], index=False)

    # 5. Analyze route performance.
    route = calculate_metrics(
        df,
        ["departure_iata", "arrival_iata"],
    )
    route = route.sort_values(
        "observations",
        ascending=False,
    )
    route.to_csv(OUTPUT_FILES["route"], index=False)

    # 6. Save a valid JSON summary.
    with open(
        OUTPUT_FILES["summary"],
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
            allow_nan=False,
        )

    # 7. Print execution results.
    logging.info("FLIGHT PULSE ANALYTICS COMPLETED")
    logging.info(
        "Total observations: %s",
        summary["total_observations"],
    )
    logging.info(
        "Airlines: %s",
        summary["unique_airlines"],
    )
    logging.info(
        "Departure airports: %s",
        summary["unique_departure_airports"],
    )
    logging.info(
        "Routes: %s",
        summary["unique_routes"],
    )
    logging.info("Analytics files saved to: %s", PROCESSED_DIR)


if __name__ == "__main__":
    main()
