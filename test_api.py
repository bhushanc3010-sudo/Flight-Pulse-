
import requests
from config.settings import API_KEY, BASE_URL

def test_flight_api():
    if not API_KEY:
        print("ERROR: API key is missing. Check your .env file.")
        return

    # One request only; no historical data.
    params = {
        "access_key": API_KEY,
        "dep_iata": "BOM",
        "limit": 10,
        "offset": 0,
    }

    print("Testing Aviationstack live flight API...")
    print("Airport filter: BOM")
    print("Historical data: disabled")

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30,
        )

        print("HTTP status:", response.status_code)

        try:
            payload = response.json()
        except ValueError:
            print("ERROR: API returned a non-JSON response.")
            return

        if not response.ok:
            print("HTTP request failed. Check your connection and plan.")
            return

        if payload.get("error"):
            error = payload["error"]
            print("API error code:", error.get("code", "unknown"))
            print("API error message:", error.get("message", "No message"))
            return

        flights = payload.get("data")

        if not isinstance(flights, list):
            print("Unexpected API response structure.")
            print("Top-level fields:", list(payload.keys()))
            return

        print("Request successful!")
        print("Records returned:", len(flights))
        print("Pagination:", payload.get("pagination", {}))

        if flights:
            first = flights[0]

            # Show only a few non-secret fields for inspection.
            print("\nFirst flight preview:")
            print("Flight number:", first.get("flight", {}).get("iata"))
            print("Airline:", first.get("airline", {}).get("name"))
            print("Status:", first.get("flight_status"))
            print("Departure airport:", first.get("departure", {}).get("airport"))
            print("Scheduled departure:", first.get("departure", {}).get("scheduled"))
        else:
            print("No matching flights returned for this request.")

    except requests.RequestException as exc:
        # Do not print the full request URL; it contains the API key.
        print("Network error:", type(exc).__name__)
        print("Check your internet connection and try again.")

if __name__ == "__main__":
    test_flight_api()