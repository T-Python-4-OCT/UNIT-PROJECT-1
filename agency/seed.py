from agency.config import BOOKINGS_FILE, COUNTRIES_FILE, USERS_FILE
from agency.countries_data import COUNTRIES
from agency.services import promos
from agency.storage import json_db
from agency.utils.security import hash_password

COUNTRY_KEYS = ["id", "country", "city", "category", "flight", "hotel", "food",
                "transport", "activities", "best_season", "highlights"]


# تنشئ ملفات البيانات أول تشغيل مع حساب admin.
def run() -> None:
    if not USERS_FILE.exists():
        json_db.save(USERS_FILE, [{
            "id": 1,
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "full_name": "Agency Manager",
            "email": "admin@skyroute.com",
            "role": "manager",
        }])

    if not COUNTRIES_FILE.exists():
        rows = [(i, *row) for i, row in enumerate(COUNTRIES, start=1)]
        json_db.save(COUNTRIES_FILE, [dict(zip(COUNTRY_KEYS, row)) for row in rows])

    if not BOOKINGS_FILE.exists():
        json_db.save(BOOKINGS_FILE, [])

    promos.seed()
