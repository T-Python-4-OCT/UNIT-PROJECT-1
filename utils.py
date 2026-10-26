"""
utils.py
Helper functions for printing, menus, and input validation.
"""
import re
import time
from datetime import datetime

import questionary
from questionary import Choice, Style
from rich.console import Console
from rich.panel import Panel

console = Console()


class InputCancelled(Exception):
    pass


# Styles for questionary menus and inputs
MENU_STYLE = Style([
    ("qmark", "fg:yellow bold"),
    ("question", "fg:white bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "bold"),
])

TEXT_STYLE = Style([
    ("qmark", "fg:yellow bold"),
    ("question", "fg:white bold"),
    ("answer", "fg:cyan bold"),
])


# Print helpers
def print_header(title, subtitle=""):
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]", border_style="cyan"))

def print_success(message):
    console.print(f"[bold green]✅ {message}[/bold green]")

def print_error(message):
    console.print(f"[bold red]❌ {message}[/bold red]")

def print_info(message):
    console.print(f"[bold yellow]ℹ️  {message}[/bold yellow]")

def show_spinner(text="Loading..."):
    with console.status(f"[bold cyan]⏳ {text}[/bold cyan]", spinner="dots"):
        time.sleep(0.5)

def render_progress_bar(percentage, width=14):
    # Build a simple text progress bar based on the percentage
    filled = int(round((percentage / 100) * width))
    filled = max(0, min(width, filled))
    bar = "█" * filled + "░" * (width - filled)
    color = "green" if percentage >= 80 else ("cyan" if percentage >= 50 else "yellow")
    return f"[{color}]{bar} {percentage}%[/{color}]"


# Menu helpers
def prompt_select(message, choices):
    return questionary.select(message, choices=choices, style=MENU_STYLE).ask()

def prompt_confirm(message="Are you sure you want to delete this item?"):
    choices = [
        Choice(title=[("fg:white", "🔙 No, Cancel")], value=False),
        Choice(title=[("fg:ansired bold", "🗑️  Yes, Delete")], value=True),
    ]
    result = questionary.select(message, choices=choices, style=MENU_STYLE).ask()
    return bool(result)

def confirm_delete(message="Are you sure you want to delete this item?"):
    return prompt_confirm(message)


# Base input functions
def _ask(question):
    answer = question.ask()
    if answer is None:
        raise InputCancelled()
    return answer

def _read_text(message, default_value=""):
    return str(_ask(questionary.text(message, default=str(default_value), style=TEXT_STYLE))).strip()

def _prompt_validated(message, default_value, validator):
    # Keep asking until the user enters a valid input
    while True:
        value = _read_text(message, default_value)
        if not value:
            print_error("This field cannot be empty. Please enter a value.")
            continue
        ok, result = validator(value)
        if ok:
            return result
        print_error(result)


# Text validation
def _check_text(value):
    if not any(ch.isalpha() for ch in value):
        return False, "Please enter text (letters). Numbers or symbols only are not allowed."
    return True, value

def _check_name(value):
    if any(ch.isdigit() for ch in value):
        return False, "This field cannot contain numbers. Please enter letters only."
    if not any(ch.isalpha() for ch in value):
        return False, "Please enter a valid name using letters."
    if not all(ch.isalpha() or ch in " .'-&" for ch in value):
        return False, "Only letters, spaces, and . ' - & are allowed."
    return True, value

def _check_username(value):
    if not all(ch.isalnum() or ch in "_.-" for ch in value):
        return False, "Username can only contain letters, numbers, and _ . - (no spaces)."
    return True, value

def _check_course_code(value):
    if not value.isalnum():
        return False, "Course code can only contain letters and numbers."
    if not any(ch.isalpha() for ch in value):
        return False, "Course code must contain at least one letter (e.g., SWE301)."
    if not 2 <= len(value) <= 10:
        return False, "Course code must be between 2 and 10 characters."
    return True, value.upper()


def prompt_required_text(message, default_value=""):
    while True:
        value = _read_text(message, default_value)
        if value:
            return value
        print_error("This field cannot be empty. Please enter a value.")

def prompt_text(message, default_value=""):
    return _prompt_validated(message, default_value, _check_text)

def prompt_name(message, default_value=""):
    return _prompt_validated(message, default_value, _check_name)

def prompt_username(message, default_value=""):
    return _prompt_validated(message, default_value, _check_username)

def prompt_course_code(message, default_value=""):
    return _prompt_validated(message, default_value, _check_course_code)


# Number validation
def prompt_int_range(message, min_val=1, max_val=None, default_value=None):
    def check(value):
        if not re.fullmatch(r"[+-]?\d+", value):
            return False, "Please enter a whole number (digits only)."
        number = int(value)
        if number < min_val or (max_val is not None and number > max_val):
            limit = f"between {min_val} and {max_val}" if max_val is not None else f"{min_val} or more"
            return False, f"The number must be {limit}."
        return True, number

    default = min_val if default_value is None else default_value
    return _prompt_validated(message, default, check)

def prompt_positive_int(message, default_val=1, default_value=None):
    if default_value is not None:
        default_val = default_value
    return prompt_int_range(message, 1, None, default_val)

def prompt_float_range(message, min_val=0.0, max_val=None, default_value=None, min_exclusive=False):
    def check(value):
        if not re.fullmatch(r"[+-]?\d+(\.\d+)?", value):
            return False, "Please enter a valid number (e.g., 85 or 85.5)."
        number = float(value)
        too_low = number <= min_val if min_exclusive else number < min_val
        too_high = max_val is not None and number > max_val
        if too_low or too_high:
            low_text = f"greater than {min_val:g}" if min_exclusive else f"at least {min_val:g}"
            if max_val is not None:
                return False, f"The number must be {low_text} and not more than {max_val:g}."
            return False, f"The number must be {low_text}."
        return True, number

    default = min_val if default_value is None else default_value
    return _prompt_validated(message, default, check)


# Date, time, and password validation
def prompt_date(message, default_value=""):
    def check(value):
        try:
            return True, datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return False, "Invalid date. Please use YYYY-MM-DD format (e.g., 2026-12-15)."
    return _prompt_validated(message, default_value, check)

def prompt_time(message, default_value="09:00"):
    def check(value):
        try:
            return True, datetime.strptime(value, "%H:%M").strftime("%H:%M")
        except ValueError:
            return False, "Invalid time. Please use 24-hour HH:MM format (e.g., 14:30)."
    return _prompt_validated(message, default_value, check)

def prompt_password(message, min_length=1):
    while True:
        value = _ask(questionary.password(message, style=TEXT_STYLE))
        if not value.strip():
            print_error("Password cannot be empty.")
        elif len(value.strip()) < min_length:
            print_error(f"Password must be at least {min_length} characters long.")
        else:
            return value