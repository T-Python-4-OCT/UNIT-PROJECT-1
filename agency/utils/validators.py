import re
from datetime import date, datetime

from agency.errors import ServiceError

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME = re.compile(r"^[A-Za-z0-9_]{3,20}$")
_CVV = re.compile(r"^\d{3,4}$")


# تتأكد أن شكل الإيميل صحيح (نص@نص.نص).
def is_valid_email(value: str) -> bool:
    return bool(_EMAIL.match(value))


# تتأكد أن الاسم الكامل من 2 إلى 60 حرف.
def is_valid_full_name(value: str) -> bool:
    value = value.strip()
    return 2 <= len(value) <= 60 and value.isprintable()


# تنظف رقم الجوال وترجعه بصيغة موحدة (8-15 رقم).
def normalize_phone(value: str) -> str:
    cleaned = re.sub(r"[\s\-().]", "", value.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    digits = cleaned[1:] if cleaned.startswith("+") else cleaned
    return cleaned if digits.isdigit() and 8 <= len(digits) <= 15 else ""


# تتأكد أن اسم المستخدم من 3 إلى 20 حرف: حروف إنجليزية وأرقام و _ فقط.
def is_valid_username(value: str) -> bool:
    return bool(_USERNAME.match(value))


# تتأكد أن كلمة السر 6 أحرف على الأقل.
def is_valid_password(value: str) -> bool:
    return len(value) >= 6


# تتأكد أن اسم صاحب البطاقة حروف فقط (3 على الأقل).
def is_valid_card_holder(value: str) -> bool:
    value = value.strip()
    return (sum(ch.isalpha() for ch in value) >= 3
            and all(ch.isalpha() or ch in " .'-" for ch in value))


# تتأكد أن رمز CVV من 3 أو 4 أرقام.
def is_valid_cvv(value: str) -> bool:
    return bool(_CVV.match(value))


# تتأكد أن رقم البطاقة من 8 إلى 16 رقم.
def is_valid_card_number(value: str) -> bool:
    digits = value.replace(" ", "").replace("-", "")
    return digits.isdigit() and 8 <= len(digits) <= 16


# تتأكد أن كود الخصم 3-15 حرف أو رقم إنجليزي.
def is_valid_promo_code(value: str) -> bool:
    return value.isalnum() and value.isascii() and 3 <= len(value) <= 15


# تحوّل نص التاريخ إلى تاريخ وتتأكد أنه في المستقبل.
def parse_future_date(text: str) -> str:
    try:
        parsed = datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ServiceError("Date must look like YYYY-MM-DD, for example 2026-12-25.")
    if parsed <= date.today():
        raise ServiceError("Travel date must be in the future.")
    return parsed.isoformat()
