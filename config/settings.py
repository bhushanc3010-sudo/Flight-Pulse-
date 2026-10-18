
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

# Load variables from the exact .env path
load_dotenv(dotenv_path=ENV_FILE, override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "").strip()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY", "").strip()

BASE_URL = "https://api.aviationstack.com/v1/flights"

AIRPORTS = [
    code.strip().upper()
    for code in os.getenv(
        "FLIGHT_AIRPORTS", "DEL"
    ).split(",")
    if code.strip()
]

MAX_AIRPORTS_PER_RUN = int(
    os.getenv("MAX_AIRPORTS_PER_RUN", "2")
)

ENABLE_HISTORICAL = False

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
LOG_DIR = PROJECT_ROOT / "logs"
EXPORT_DIR = PROJECT_ROOT / "exports"

for directory in [
    RAW_DIR,
    PROCESSED_DIR,
    LOG_DIR,
    EXPORT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)