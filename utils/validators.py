import math

from utils import display


def get_text(prompt):
    """Ask until the user types a non-empty text."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
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