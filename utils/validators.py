import math
from datetime import date, datetime

from utils import display


def get_text(prompt, allow_blank=False):
    """Ask until the user types a non-empty text.

    If allow_blank is True, pressing Enter returns None (keep the old value).
    """
    while True:
        text = input(prompt).strip()
        if text:
            return text
        if allow_blank:
            return None
        display.print_error("This field cannot be empty.")


def get_positive_number(prompt, allow_blank=False):
    """Ask until the user types a number greater than zero.

    If allow_blank is True, pressing Enter returns None (keep the old value).
    """
    while True:
        raw_value = input(prompt).strip()
        if allow_blank and raw_value == "":
            return None
        try:
            number = float(raw_value)
        except ValueError:
            display.print_error("Invalid input. Please enter a number.")
            continue
        if not math.isfinite(number) or number <= 0:
            display.print_error("The number must be greater than zero.")
            continue
        return int(number) if number.is_integer() else number


def get_menu_choice(prompt, valid_choices):
    """Ask until the user types one of the valid choices (as text)."""
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        display.print_error(f"Invalid choice. Please enter one of: {', '.join(valid_choices)}.")


def get_number_in_range(prompt, low, high):
    """Ask until the user types a whole number between low and high (inclusive)."""
    valid_choices = [str(number) for number in range(low, high + 1)]
    return int(get_menu_choice(prompt, valid_choices))


def confirm(prompt):
    """Ask a yes/no question. Return True for yes."""
    answer = get_menu_choice(f"{prompt} (y/n): ", ["y", "n", "Y", "N"])
    return answer.lower() == "y"


def get_date(prompt):
    """Ask for a date as YYYY-MM-DD. Enter means today. Future dates are rejected."""
    while True:
        raw_value = input(prompt).strip()
        if raw_value == "":
            return date.today().isoformat()
        try:
            chosen = datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError:
            display.print_error("Invalid date. Use the format YYYY-MM-DD (for example 2026-10-21).")
            continue
        if chosen > date.today():
            display.print_error("The date cannot be in the future.")
            continue
        return chosen.isoformat()


def get_number(prompt, low, high, allow_blank=False):
    """Ask for any number between low and high (inclusive).

    If allow_blank is True, pressing Enter returns None (keep the old value).
    """
    while True:
        raw_value = input(prompt).strip()
        if allow_blank and raw_value == "":
            return None
        try:
            number = float(raw_value)
        except ValueError:
            display.print_error("Invalid input. Please enter a number.")
            continue
        if not math.isfinite(number) or not low <= number <= high:
            display.print_error(f"The number must be between {low} and {high}.")
            continue
        return int(number) if number.is_integer() else number