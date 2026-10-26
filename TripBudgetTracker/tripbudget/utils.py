"""Small helpers (Lesson 5: functions, Lesson 8: lambda + decorators)."""
import functools
import math

from .errors import TripError

# Lambda: format a number as money, e.g. 1800 -> "1,800.00 SAR"
format_money = lambda amount, currency: f"{amount:,.2f} {currency}"

# Support Arabic-Indic (٠١٢...) and Persian (۰۱۲...) digits.
_DIGIT_TRANSLATION = {
    **{ord(chr(0x0660 + i)): str(i) for i in range(10)},
    **{ord(chr(0x06F0 + i)): str(i) for i in range(10)},
    ord("٫"): ".",  # Arabic decimal separator
    ord("٬"): "",   # Arabic thousands separator
}


def normalize_digits(text: str) -> str:
    return text.translate(_DIGIT_TRANSLATION)


def is_finite_number(value: float) -> bool:
    """Reject NaN and infinity before they enter budget calculations."""
    return math.isfinite(value)


def progress_bar(spent: float, budget: float, width: int = 20) -> str:
    """Text bar like [########------------]  40%"""
    ratio = min(spent / budget, 1) if budget > 0 else 0
    filled = int(ratio * width)
    percent = (spent / budget * 100) if budget > 0 else 0
    return f"[{'#' * filled}{'-' * (width - filled)}] {percent:>4.0f}%"


def safe_action(func):
    """Decorator: show friendly errors instead of crashing the whole program."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TripError as err:
            print(f"\n  !! {err}\n")
            return None
    return wrapper
