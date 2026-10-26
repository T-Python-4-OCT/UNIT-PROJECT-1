"""Everything that checks input: what the user types, and what is read from the data file."""
import math
from datetime import date, datetime

import questionary

from guardian.display import MENU_STYLE, POINTER, console
from guardian.subscription import CATEGORIES, CYCLES

MAX_NAME_LENGTH = 30
MAX_PRICE = 100_000
MAX_MONTHS = 60
OLDEST_START_DATE = date(2000, 1, 1)


# ---------- Rules (return an error message, or None if the value is fine) ----------

def name_error(name: str, taken_names: list[str] = ()) -> str | None:
    if not name:
        return "The name can't be empty."
    if len(name) > MAX_NAME_LENGTH:
        return f"The name can't be longer than {MAX_NAME_LENGTH} characters."
    if name.lower() in [taken.lower() for taken in taken_names]:
        return f'You already have a subscription called "{name}".'
    return None


def price_error(price: float) -> str | None:
    if not math.isfinite(price):  # catches "nan" and "inf"
        return "Price must be a real number (example: 45 or 12.5)."
    if price <= 0:
        return "Price must be more than 0."
    if price > MAX_PRICE:
        return f"Price can't be more than {MAX_PRICE:,} SAR."
    if round(price, 2) != price:
        return "Price can have at most 2 digits after the dot (example: 12.50)."
    return None


def months_error(months: int) -> str | None:
    if months < 1 or months > MAX_MONTHS:
        return f"The number of months must be from 1 to {MAX_MONTHS}."
    return None


def start_date_error(start_date: date) -> str | None:
    if start_date > date.today():
        return "The start date can't be in the future."
    if start_date < OLDEST_START_DATE:
        return f"The start date can't be before {OLDEST_START_DATE}."
    return None


def subscription_data_error(data: dict, taken_names: list[str] = ()) -> str | None:
    """Check one subscription read from the JSON file."""
    try:
        start_date = date.fromisoformat(data["start_date"])
        price = float(data["price"])
        name = data["name"].strip()
    except (KeyError, ValueError, TypeError, AttributeError):
        return "missing or broken fields"

    if data.get("cycle") not in CYCLES:
        return f"unknown cycle {data.get('cycle')!r}"
    if data.get("category") not in CATEGORIES:
        return f"unknown category {data.get('category')!r}"
    if data["cycle"] == "custom":
        months = data.get("months")
        if not isinstance(months, int) or isinstance(months, bool):
            return "a custom subscription needs a whole number of months"
        if months_error(months):
            return months_error(months)
    return name_error(name, taken_names) or price_error(price) or start_date_error(start_date)


# ---------- Asking the user (ask again with recursion until the answer is valid) ----------

def ask_name(message: str, taken_names: list[str] = ()) -> str:
    """Ask for a subscription name that is not empty, not too long, and not used before."""
    name = input(message).strip()
    error = name_error(name, taken_names)
    if error:
        console.print(f"[red]{error}[/red]")
        return ask_name(message, taken_names)
    return name


def ask_price(message: str) -> float:
    """Ask for a price between 0 and MAX_PRICE with at most 2 decimals."""
    try:
        price = float(input(message))
    except ValueError:
        console.print("[red]Price must be a number (example: 45 or 12.5).[/red]")
        return ask_price(message)

    error = price_error(price)
    if error:
        console.print(f"[red]{error}[/red]")
        return ask_price(message)
    return price


def ask_months(message: str) -> int:
    """Ask for a whole number of months from 1 to MAX_MONTHS."""
    try:
        months = int(input(message))
    except ValueError:
        console.print("[red]Enter a whole number of months (example: 6 or 18).[/red]")
        return ask_months(message)

    error = months_error(months)
    if error:
        console.print(f"[red]{error}[/red]")
        return ask_months(message)
    return months


def ask_date(message: str) -> date:
    """Ask for a date in the format YYYY-MM-DD."""
    text = input(message).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]Wrong date, use YYYY-MM-DD (example: 2026-11-05).[/red]")
        return ask_date(message)


def ask_start_date(message: str) -> date:
    """Ask for the date the subscription started (between OLDEST_START_DATE and today)."""
    start_date = ask_date(message)
    error = start_date_error(start_date)
    if error:
        console.print(f"[red]{error}[/red]")
        return ask_start_date(message)
    return start_date


def ask_confirm(message: str) -> bool:
    """Ask a yes/no question (No is the default, Ctrl+C counts as No)."""
    answer = questionary.confirm(message, default=False, style=MENU_STYLE).ask()
    return answer is True


def ask_choice(message: str, options: tuple | list):
    """Show a list the user picks from with the arrow keys (None if Ctrl+C)."""
    return questionary.select(
        message,
        choices=list(options),
        use_shortcuts=True,
        pointer=POINTER,
        style=MENU_STYLE,
    ).ask()
