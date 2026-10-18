
import json
import logging
from datetime import datetime, timezone

import requests

from config.settings import API_KEY, BASE_URL, RAW_DIR

logger = logging.getLogger(__name__)


def fetch_live_flights(
    airport="BOM",
    limit=10,
    direction="departure",
):
    """Fetch one page of live flights and preserve the raw response."""

    if not API_KEY:
        raise ValueError("API key is missing from .env")

    airport = airport.strip().upper()

    if direction not in {"departure", "arrival"}:
        raise ValueError("direction must be departure or arrival")

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    filter_name = (
        "dep_iata" if direction == "departure" else "arr_iata"
    )

    params = {
        "access_key": API_KEY,
        filter_name: airport,
        "limit": limit,
        "offset": 0,
    }

    retrieved_at = datetime.now(timezone.utc)

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30,
        )
    except requests.RequestException as exc:
        # Do not log the URL because it contains the API key.
        raise RuntimeError(
            f"Network request failed: {type(exc).__name__}"
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"API returned non-JSON content; HTTP {response.status_code}"
        ) from exc

    if not response.ok:
        raise RuntimeError(
            f"HTTP error: {response.status_code}"
        )

    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected API response type")

    if payload.get("error"):
        error = payload["error"]
        raise RuntimeError(
            "Aviationstack error: "
            f"{error.get('code', 'unknown')} - "
            f"{error.get('message', 'No message')}"
        )

    records = payload.get("data")

    if not isinstance(records, list):
        raise RuntimeError("Expected a list in the API 'data' field")

    # Keep the original API response unchanged.
    timestamp = retrieved_at.strftime("%Y%m%dT%H%M%SZ")
    filename = (
        f"flights_{airport}_{direction}_{timestamp}.json"
    )
    filepath = RAW_DIR / filename

    saved_data = {
        "ingestion_metadata": {
            "provider": "Aviationstack",
            "retrieved_at_utc": retrieved_at.isoformat(),
            "airport": airport,
            "direction": direction,
            "requested_limit": limit,
            "historical_data_requested": False,
        },
        "api_response": payload,
    }

    filepath.write_text(
        json.dumps(saved_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logger.info(
        "Saved %d records for %s to %s",
        len(records),
        airport,
        filepath.name,
    )

    return {
        "airport": airport,
        "direction": direction,
        "record_count": len(records),
        "provider_total": payload.get("pagination", {}).get("total"),
        "raw_file": str(filepath),
    }
