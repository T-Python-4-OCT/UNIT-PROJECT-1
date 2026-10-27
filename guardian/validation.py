"""Everything that checks input: what the user types, and what is read from the data file."""
import math
import sys
from datetime import date, datetime

import questionary
from prompt_toolkit import HTML, Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.layout import BufferControl, FormattedTextControl, HSplit, Layout, VSplit, Window

from guardian.display import MENU_STYLE, POINTER, console
from guardian.subscription import CATEGORIES, CYCLES, IMPORTANCE_LEVELS

MAX_NAME_LENGTH = 30
MAX_PRICE = 100_000
MAX_MONTHS = 60
OLDEST_START_DATE = date(2000, 1, 1)


# ---------- Rules (return an error message, or None if the value is fine) ----------

def name_error(name: str, taken_names: list[str] = ()) -> str | None:
    """A name must not be empty, not too long, and not used by another subscription."""
    if not name:
        return "The name can't be empty."
    if len(name) > MAX_NAME_LENGTH:
        return f"The name can't be longer than {MAX_NAME_LENGTH} characters."
    if name.lower() in [taken.lower() for taken in taken_names]:
        return f'You already have a subscription called "{name}".'
    return None


def price_error(price: float) -> str | None:
    """A price must be a real number between 0 and MAX_PRICE with at most 2 decimals."""
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
    """A custom cycle must be from 1 to MAX_MONTHS months."""
    if months < 1 or months > MAX_MONTHS:
        return f"The number of months must be from 1 to {MAX_MONTHS}."
    return None


def start_date_error(start_date: date) -> str | None:
    """A start date must be between OLDEST_START_DATE and today."""
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
    if data.get("importance", "Nice to have") not in IMPORTANCE_LEVELS:
        return f"unknown importance {data.get('importance')!r}"
    if data["cycle"] == "custom":
        months = data.get("months")
        if not isinstance(months, int) or isinstance(months, bool):
            return "a custom subscription needs a whole number of months"
        if months_error(months):
            return months_error(months)
    return name_error(name, taken_names) or price_error(price) or start_date_error(start_date)


# ---------- Going back to the menu ----------

BACK = "Back"
BACK_WORD = "back"


class GoBack(Exception):
    """Raised when the user picks Back (or types 'back'), to go back."""


def read(message: str) -> str:
    """Read what the user types. A Back option is shown under it: press Down then Enter to go back."""
    if sys.stdin.isatty():
        text = prompt_with_back(message)
    else:
        text = input(message)  # when input comes from a file or a test, there is no Back line

    if text is None or text.strip().lower() == BACK_WORD:
        raise GoBack
    return text.strip()


def prompt_with_back(message: str) -> str | None:
    """Ask with a Back option right under the question. Returns None if the user picks Back."""
    back_selected = [False]  # a list so the key functions below can change it
    typed = Buffer()
    keys = KeyBindings()

    @keys.add("down")
    def select_back(event):
        back_selected[0] = True

    @keys.add("up")
    def select_typing(event):
        back_selected[0] = False

    @keys.add("enter")
    def submit(event):
        event.app.exit(result=None if back_selected[0] else typed.text)

    @keys.add("c-c")
    def cancel(event):
        event.app.exit(exception=KeyboardInterrupt)

    def back_line():
        if back_selected[0]:
            return HTML(f'<style fg="#5c9dff"><b>{POINTER} Back</b></style>')
        return HTML("<style fg='#888888'>  Back</style>")

    # Two lines: the question with what the user types, and the Back option under it
    layout = Layout(HSplit([
        VSplit([
            Window(FormattedTextControl(message), dont_extend_width=True),
            Window(BufferControl(typed)),
        ], height=1),
        Window(FormattedTextControl(back_line), height=1),
    ]), focused_element=typed)

    app = Application(layout=layout, key_bindings=merge_key_bindings([load_key_bindings(), keys]),
                      erase_when_done=True)
    answer = app.run()

    # The two lines are erased when done, so print the question and the answer again
    if answer is not None:
        print(f"{message}{answer}")
    return answer


# ---------- Asking the user (ask again with recursion until the answer is valid) ----------

def ask_name(message: str, taken_names: list[str] = ()) -> str:
    """Ask for a subscription name that is not empty, not too long, and not used before."""
    name = read(message)
    error = name_error(name, taken_names)
    if error:
        console.print(f"[red]{error}[/red]")
        return ask_name(message, taken_names)
    return name


def ask_price(message: str) -> float:
    """Ask for a price between 0 and MAX_PRICE with at most 2 decimals."""
    try:
        price = float(read(message))
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
        months = int(read(message))
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
    text = read(message)
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


def ask_choice(message: str, options: tuple | list, back: bool = True):
    """Show a list the user picks from with the arrow keys.

    With back=True the list ends with a Back option, and picking it (or pressing Ctrl+C)
    returns to the main menu. With back=False it returns None on Ctrl+C.
    """
    choices = list(options) + ([BACK] if back else [])
    answer = questionary.select(
        message,
        choices=choices,
        use_shortcuts=True,
        pointer=POINTER,
        style=MENU_STYLE,
    ).ask()
    if back and answer in (BACK, None):
        raise GoBack
    return answer
