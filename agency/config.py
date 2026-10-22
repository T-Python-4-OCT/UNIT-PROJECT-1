import os
from pathlib import Path

APP_NAME = "SkyRoute"
CURRENCY = "SAR"
REFUND_NOTICE = "Your money will be refunded within 24 hours to 4 business days."


DEFAULT_DAYS = 7
MIN_DAYS = 2
MAX_DAYS = 30


GROUP_SIZE = 2
GROUP_DISCOUNT_PERCENT = 10
DEFAULT_PROMO_PERCENT = 20
MAX_PROMO_PERCENT = 50

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = Path(os.environ.get("SKYROUTE_DATA_DIR", BASE_DIR / "data"))

USERS_FILE = DATA_DIR / "users.json"
COUNTRIES_FILE = DATA_DIR / "countries.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"
PROMOS_FILE = DATA_DIR / "promos.json"

OUTBOX_DIR = DATA_DIR / "outbox"
ENV_FILE = BASE_DIR / ".env"
