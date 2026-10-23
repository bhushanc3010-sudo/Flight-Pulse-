
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"pipeline_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

STEPS = [
    ("EXTRACT", [sys.executable, "-m", "src.acquisition.run_acquisition"]),
    ("TRANSFORM", [sys.executable, "-m", "src.cleaning.run_cleaning"]),
    ("LOAD", [sys.executable, "-m", "src.database.load_flights"]),
]


def run_step(step_name, command):
    logging.info("=" * 55)
    logging.info("Starting step: %s", step_name)

    start_time = time.perf_counter()

    try:
        subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        logging.error(
            "Step %s failed with exit code %s",
            step_name,
            error.returncode,
        )
        raise

    elapsed = time.perf_counter() - start_time
    logging.info(
        "Step %s completed successfully in %.2f seconds",
        step_name,
        elapsed,
    )


def main():
    pipeline_start = time.perf_counter()
    logging.info("FLIGHT PULSE PIPELINE STARTED")
    logging.info("Log file: %s", LOG_FILE)

    try:
        for step_name, command in STEPS:
            run_step(step_name, command)

        elapsed = time.perf_counter() - pipeline_start
        logging.info("=" * 55)
        logging.info("PIPELINE COMPLETED SUCCESSFULLY")
        logging.info("Total runtime: %.2f seconds", elapsed)

    except (subprocess.CalledProcessError, OSError):
        logging.exception("PIPELINE FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
