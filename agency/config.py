"""Paths and constants shared by the whole app."""
import os
from pathlib import Path

APP_NAME = "SkyRoute"
CURRENCY = "SAR"
REFUND_NOTICE = "Your money will be refunded within 24 hours to 4 business days."
SUPPORT_EMAIL = "support@skyroute.example"    # a made-up company address (.example is reserved for demos)

# Trip length: 7 days is the suggested default, but the customer may choose any length.
DEFAULT_DAYS = 7
MIN_DAYS = 2
MAX_DAYS = 30

# Discounts: two travelers get 10% off; the manager's occasion codes default to 20%.
GROUP_SIZE = 2
GROUP_DISCOUNT_PERCENT = 10
DEFAULT_PROMO_PERCENT = 20
YEAR_END_PROMO_PERCENT = 10
MAX_PROMO_PERCENT = 50

BASE_DIR = Path(__file__).resolve().parent.parent
# SKYROUTE_DATA_DIR lets the tests use a temporary folder.
DATA_DIR = Path(os.environ.get("SKYROUTE_DATA_DIR", BASE_DIR / "data"))

USERS_FILE = DATA_DIR / "users.json"
COUNTRIES_FILE = DATA_DIR / "countries.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"
PROMOS_FILE = DATA_DIR / "promos.json"

OUTBOX_DIR = DATA_DIR / "outbox"     # copies of emails that were not sent through SMTP
ENV_FILE = BASE_DIR / ".env"         # optional file with the SMTP settings (never uploaded to Git)
