from datetime import datetime

from .errors import ClinicError

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_date(text):
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        raise ClinicError("Invalid date. Use YYYY-MM-DD (e.g. 2026-11-03).")


def parse_time(text):
    try:
        return datetime.strptime(text.strip(), "%H:%M").strftime("%H:%M")
    except (ValueError, AttributeError):
        raise ClinicError("Invalid time. Use HH:MM (e.g. 10:30).")


def parse_int(text, label="value"):
    try:
        return int(str(text).strip())
    except ValueError:
        raise ClinicError(f"Invalid {label}: '{text}' must be a number.")


def parse_day(text):
    day = text.strip().lower()
    if day not in WEEKDAYS:
        raise ClinicError(f"Invalid day '{text}'. Use one of: {', '.join(WEEKDAYS)}.")
    return day