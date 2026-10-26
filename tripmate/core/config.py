"""Central settings for TripMate."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


# ---------- Storage ----------

DATA_FOLDER = BASE_DIR / "data"

TRIPS_FILE = DATA_FOLDER / "trips.json"

EXPENSES_FILE = DATA_FOLDER / "expenses.json"

EXPORT_FOLDER = BASE_DIR / "exports"


# ---------- Money ----------

CURRENCY = "SAR"

BUDGET_WARNING_PERCENT = 80


EXPENSE_CATEGORIES = [
    "Accommodation",
    "Transport",
    "Food",
    "Activities",
    "Shopping",
    "Other",
]


# ---------- Dates ----------

MAX_YEARS_AHEAD = 10


# ---------- Weather ----------

FORECAST_DAYS_LIMIT = 16

REQUEST_TIMEOUT = 10


# ---------- AI ----------

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)