"""Input checks: email, phone, username, password, card number, promo code, dates."""
import re
from datetime import date, datetime

from agency.errors import ServiceError

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME = re.compile(r"^[A-Za-z0-9_]{3,20}$")
_CVV = re.compile(r"^\d{3,4}$")


def is_valid_email(value: str) -> bool:
    """Simple email shape check."""
    return bool(_EMAIL.match(value))


def is_valid_full_name(value: str) -> bool:
    """2-60 characters, no control characters (so it is safe inside an email subject)."""
    value = value.strip()
    return 2 <= len(value) <= 60 and value.isprintable()


def normalize_phone(value: str) -> str:
    """Clean a mobile number: spaces, dashes, dots and brackets are removed and a leading
    00 becomes +. Returns "" when it is not 8-15 digits (optionally starting with +)."""
    cleaned = re.sub(r"[\s\-().]", "", value.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    digits = cleaned[1:] if cleaned.startswith("+") else cleaned
    return cleaned if digits.isdigit() and 8 <= len(digits) <= 15 else ""


def is_valid_username(value: str) -> bool:
    """3-20 characters: letters, numbers or underscore."""
    return bool(_USERNAME.match(value))


def is_valid_password(value: str) -> bool:
    """At least 6 characters."""
    return len(value) >= 6


def is_valid_card_holder(value: str) -> bool:
    """A real-looking name: at least 3 letters, and only letters, spaces or . ' - (no digits)."""
    value = value.strip()
    return (sum(ch.isalpha() for ch in value) >= 3
            and all(ch.isalpha() or ch in " .'-" for ch in value))


def is_valid_cvv(value: str) -> bool:
    """3 or 4 digits."""
    return bool(_CVV.match(value))


def is_valid_card_number(value: str) -> bool:
    """8 to 16 digits (spaces and dashes are allowed between them)."""
    digits = value.replace(" ", "").replace("-", "")
    return digits.isdigit() and 8 <= len(digits) <= 16


def is_valid_promo_code(value: str) -> bool:
    """3-15 characters: letters and numbers only (the code is stored in upper case)."""
    return value.isalnum() and value.isascii() and 3 <= len(value) <= 15


def parse_future_date(text: str) -> str:
    """Return the date as YYYY-MM-DD, or raise if invalid or not in the future."""
    try:
        parsed = datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ServiceError("Date must look like YYYY-MM-DD, for example 2026-12-25.")
    if parsed <= date.today():
        raise ServiceError("Travel date must be in the future.")
    return parsed.isoformat()
