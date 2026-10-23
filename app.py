
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from config.settings import PROCESSED_DIR


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Flight Pulse | Flight Intelligence",
    page_icon="✈️",
    layout="wide",
)

INPUT_FILE = PROCESSED_DIR / "flights_cleaned.csv"
SUMMARY_FILE = PROCESSED_DIR / "analytics_summary.json"


# --------------------------------------------------
# Load data
# --------------------------------------------------

@st.cache_data
def load_flights(file_path, modified_time):
    """Load the latest cleaned flight dataset."""
    return pd.read_csv(file_path)


def calculate_delay_rate(data):
    """Calculate delay rate using only known outcomes."""
    known = data["delay_status"].isin(
        ["Delayed", "Not delayed"]
    )
    known_count = int(known.sum())

    if known_count == 0:
        return None

    delayed_count = int(
        data["delay_status"].eq("Delayed").sum()
    )

    return delayed_count / known_count * 100


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("✈️ Flight Pulse")
st.subheader("Flight Delay Intelligence Dashboard")

st.caption(
    "Explore observed flight activity, delay patterns, "
    "airline performance, and airport operations."
)

if not INPUT_FILE.exists():
    st.error(
        "Cleaned flight data was not found. "
        "Run the Flight Pulse pipeline first."
    )
    st.stop()

last_modified = INPUT_FILE.stat().st_mtime

try:
    df = load_flights(str(INPUT_FILE), last_modified)
except Exception as error:
    st.error(f"Could not load the cleaned dataset: {error}")
    st.stop()

if df.empty:
    st.warning("The cleaned flight dataset is empty.")
    st.stop()


# --------------------------------------------------
# Validate and prepare data
# --------------------------------------------------

required_columns = [
    "airline",
    "departure_iata",
    "arrival_iata",
    "departure_delay_minutes",
    "delay_status",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

for column in [
    "airline",
    "departure_iata",
    "arrival_iata",
    "delay_status",
]:
    df[column] = df[column].fillna("Unknown").astype(str)

df["departure_delay_minutes"] = pd.to_numeric(
    df["departure_delay_minutes"],
    errors="coerce",
)

# Remove invalid numeric values from delay calculations.
df.loc[
    ~df["departure_delay_minutes"].between(-10000, 10000),
    "departure_delay_minutes",
] = float("nan")


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

airline_options = sorted(df["airline"].unique().tolist())
departure_options = sorted(
    df["departure_iata"].unique().tolist()
)
arrival_options = sorted(
    df["arrival_iata"].unique().tolist()
)
status_options = sorted(df["delay_status"].unique().tolist())

selected_airlines = st.sidebar.multiselect(
    "Airline",
    airline_options,
    default=airline_options,
)

selected_departures = st.sidebar.multiselect(
    "Departure airport",
    departure_options,
    default=departure_options,
)

selected_arrivals = st.sidebar.multiselect(
    "Arrival airport",
    arrival_options,
    default=arrival_options,
)

selected_statuses = st.sidebar.multiselect(
    "Delay status",
    status_options,
    default=status_options,
)

filtered_df = df[
    df["airline"].isin(selected_airlines)
    & df["departure_iata"].isin(selected_departures)
    & df["arrival_iata"].isin(selected_arrivals)
    & df["delay_status"].isin(selected_statuses)
].copy()

st.sidebar.divider()
st.sidebar.caption(
    "Filters apply to the collected observations currently "
    "available in the cleaned dataset."
)


# --------------------------------------------------
# KPI cards
# --------------------------------------------------

st.header("Flight Performance Overview")

total_observations = len(filtered_df)
delayed_flights = int(
    filtered_df["delay_status"].eq("Delayed").sum()
)
known_outcomes = int(
    filtered_df["delay_status"].isin(
        ["Delayed", "Not delayed"]
    ).sum()
)

delay_rate = calculate_delay_rate(filtered_df)

average_delay = filtered_df[
    "departure_delay_minutes"
].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Flight Observations",
    f"{total_observations:,}",
)

col2.metric(
    "Delayed Observations",
    f"{delayed_flights:,}",
)

col3.metric(
    "Known-Outcome Delay Rate",
    f"{delay_rate:.1f}%" if delay_rate is not None else "N/A",
)

col4.metric(
    "Average Departure Delay",
    f"{average_delay:.1f} min"
    if pd.notna(average_delay)
    else "N/A",
)

st.caption(
    f"Known delay outcomes: {known_outcomes:,} of "
    f"{total_observations:,} observations. "
    "Unknown outcomes are excluded from the delay-rate denominator."
)

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# --------------------------------------------------
# Airline analysis
# --------------------------------------------------

st.divider()
st.header("Airline Performance")

airline_metrics = (
    filtered_df.groupby("airline", dropna=False)
    .agg(
        observations=("delay_status", "size"),
        delayed_records=(
            "delay_status",
            lambda values: values.eq("Delayed").sum(),
        ),
        known_outcomes=(
            "delay_status",
            lambda values: values.isin(
                ["Delayed", "Not delayed"]
            ).sum(),
        ),
        average_delay_minutes=(
            "departure_delay_minutes",
            "mean",
        ),
    )
    .reset_index()
)

airline_metrics["delay_rate_percent"] = (
    airline_metrics["delayed_records"]
    .div(
        airline_metrics["known_outcomes"].replace(
            0, float("nan")
        )
    )
    .mul(100)
)

left, right = st.columns(2)

with left:
    st.markdown("**Flight observations by airline**")
    chart_data = airline_metrics.set_index("airline")[
        ["observations"]
    ]
    st.bar_chart(chart_data)

with right:
    st.markdown("**Observed delay rate by airline (%)**")
    rate_chart = airline_metrics.dropna(
        subset=["delay_rate_percent"]
    ).set_index("airline")[["delay_rate_percent"]]

    if not rate_chart.empty:
        st.bar_chart(rate_chart)
    else:
        st.info("There are no known delay outcomes to chart.")

st.dataframe(
    airline_metrics.round(2),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Airport analysis
# --------------------------------------------------

st.divider()
st.header("Departure Airport Analysis")

airport_metrics = (
    filtered_df.groupby("departure_iata", dropna=False)
    .agg(
        observations=("delay_status", "size"),
        delayed_records=(
            "delay_status",
            lambda values: values.eq("Delayed").sum(),
        ),
        known_outcomes=(
            "delay_status",
            lambda values: values.isin(
                ["Delayed", "Not delayed"]
            ).sum(),
        ),
        average_delay_minutes=(
            "departure_delay_minutes",
            "mean",
        ),
    )
    .reset_index()
)

airport_metrics["delay_rate_percent"] = (
    airport_metrics["delayed_records"]
    .div(
        airport_metrics["known_outcomes"].replace(
            0, float("nan")
        )
    )
    .mul(100)
)

left, right = st.columns(2)

with left:
    st.markdown("**Observations by departure airport**")
    st.bar_chart(
        airport_metrics.set_index("departure_iata")[
            ["observations"]
        ]
    )

with right:
    st.markdown("**Average departure delay (minutes)**")
    average_chart = airport_metrics.dropna(
        subset=["average_delay_minutes"]
    ).set_index("departure_iata")[["average_delay_minutes"]]

    if not average_chart.empty:
        st.bar_chart(average_chart)
    else:
        st.info("No numeric departure-delay values are available.")

st.dataframe(
    airport_metrics.round(2),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Route analysis
# --------------------------------------------------

st.divider()
st.header("Route Performance")

route_metrics = (
    filtered_df.groupby(
        ["departure_iata", "arrival_iata"],
        dropna=False,
    )
    .agg(
        observations=("delay_status", "size"),
        delayed_records=(
            "delay_status",
            lambda values: values.eq("Delayed").sum(),
        ),
        known_outcomes=(
            "delay_status",
            lambda values: values.isin(
                ["Delayed", "Not delayed"]
            ).sum(),
        ),
        average_delay_minutes=(
            "departure_delay_minutes",
            "mean",
        ),
    )
    .reset_index()
)

route_metrics["delay_rate_percent"] = (
    route_metrics["delayed_records"]
    .div(
        route_metrics["known_outcomes"].replace(
            0, float("nan")
        )
    )
    .mul(100)
)

route_metrics = route_metrics.sort_values(
    "observations",
    ascending=False,
)

st.dataframe(
    route_metrics.round(2),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Raw records and data freshness
# --------------------------------------------------

st.divider()

with st.expander("View filtered flight records"):
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

modified_datetime = datetime.fromtimestamp(last_modified)

st.caption(
    f"Cleaned dataset last modified: "
    f"{modified_datetime.strftime('%d %b %Y, %I:%M:%S %p')}"
)

st.caption(
    "Flight Pulse | Analytics based on collected observations. "
    "Results depend on API coverage, collection frequency, "
    "and the completeness of actual flight timestamps."
)
