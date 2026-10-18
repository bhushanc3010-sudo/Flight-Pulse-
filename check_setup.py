
from config.settings import (
    API_KEY,
    AIRPORTS,
    MAX_AIRPORTS_PER_RUN,
    ENABLE_HISTORICAL,
    RAW_DIR,
    PROCESSED_DIR,
    LOG_DIR,
    EXPORT_DIR,
)

print("Flight Pulse - Module 0 Setup Check")
print("-" * 40)

print("API key configured:", bool(API_KEY))
print("Selected airports:", AIRPORTS)
print("Max airports per run:", MAX_AIRPORTS_PER_RUN)
print("Historical acquisition enabled:", ENABLE_HISTORICAL)

print("Raw directory exists:", RAW_DIR.exists())
print("Processed directory exists:", PROCESSED_DIR.exists())
print("Log directory exists:", LOG_DIR.exists())
print("Export directory exists:", EXPORT_DIR.exists())

if not AIRPORTS:
    raise SystemExit("ERROR: Configure at least one airport.")

if MAX_AIRPORTS_PER_RUN < 1:
    raise SystemExit("ERROR: MAX_AIRPORTS_PER_RUN must be >= 1.")

if not API_KEY:
    print("WARNING: Add your Aviationstack key to .env.")

print("\nSetup check completed.")