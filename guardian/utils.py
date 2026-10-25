from datetime import date, datetime

import pyfiglet
import questionary
from rich.console import Console

console = Console()

# Blue colors for the lists so they match the title
MENU_STYLE = questionary.Style([
    ("qmark", "fg:#5c9dff bold"),
    ("pointer", "fg:#5c9dff bold"),
    ("highlighted", "fg:#5c9dff bold"),
    ("question", "bold"),
    ("answer", "fg:#5c9dff bold"),
    ("selected", "fg:#5c9dff"),
])
POINTER = "➜"

# Blue shades from light to dark, one for each line of the big title
BLUE_GRADIENT = (
    "#a8cfff", "#9cc7ff", "#8bbcff", "#7ab3ff", "#6aa8ff", "#5c9dff",
    "#4f93fa", "#3f86f5", "#357aeb", "#2b6fe0", "#2566db", "#1f5fd6",
)


def show_banner():
    """Print the big blue title with a gradient, and the slogan under it."""
    lines = []
    for word in ("SUBSCRIPTION", "GUARDIAN"):
        art = pyfiglet.figlet_format(word, font="ansi_shadow", width=200)
        lines += [line for line in art.splitlines() if line.strip()]

    widest = max(len(line) for line in lines)

    # The big letters need a wide window, otherwise show a simple title
    if console.width < widest:
        console.print("[bold #5c9dff]SUBSCRIPTION GUARDIAN[/]")
        console.print("[dim]Keep your money safe[/dim]\n")
        return

    for line, color in zip(lines, BLUE_GRADIENT):
        console.print(line, style=f"bold {color}", highlight=False)
    console.print("Keep your money safe".center(widest), style="dim")
    console.print()


def ask_text(message: str) -> str:
    """Ask for text that is not empty."""
    text = input(message).strip()
    if not text:
        console.print("[red]This can't be empty, try again.[/red]")
        return ask_text(message)  # recursion: ask again until valid
    return text


def ask_price(message: str) -> float:
    """Ask for a positive number."""
    try:
        price = float(input(message))
    except ValueError:
        console.print("[red]Price must be a number (example: 45 or 12.5).[/red]")
        return ask_price(message)

    if price <= 0:
        console.print("[red]Price must be more than 0.[/red]")
        return ask_price(message)
    return price


def ask_date(message: str) -> date:
    """Ask for a date in the format YYYY-MM-DD."""
    text = input(message).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]Wrong date, use YYYY-MM-DD (example: 2026-11-05).[/red]")
        return ask_date(message)


def ask_start_date(message: str) -> date:
    """Ask for the date the subscription started (today or before)."""
    start_date = ask_date(message)
    if start_date > date.today():
        console.print("[red]The start date can't be in the future.[/red]")
        return ask_start_date(message)
    return start_date


def money(amount: float) -> str:
    """Format money in a readable way: 23333 -> '23,333 SAR', 18.333 -> '18.33 SAR'."""
    amount = round(amount, 2)
    if amount == int(amount):
        return f"{int(amount):,} SAR"
    return f"{amount:,.2f} SAR"


def ask_confirm(message: str) -> bool:
    """Ask a yes/no question (No is the default, Ctrl+C counts as No)."""
    answer = questionary.confirm(message, default=False, style=MENU_STYLE).ask()
    return answer is True


def ask_checkbox(message: str, choices: list) -> list | None:
    """Show a list where the user ticks many items with Space (None if Ctrl+C)."""
    return questionary.checkbox(
        message,
        choices=choices,
        pointer=POINTER,
        style=MENU_STYLE,
        instruction="(Space to select, Enter to confirm)",
    ).ask()


def ask_choice(message: str, options: tuple | list):
    """Show a list the user picks from with the arrow keys (None if Ctrl+C)."""
    return questionary.select(
        message,
        choices=list(options),
        use_shortcuts=True,
        pointer=POINTER,
        style=MENU_STYLE,
    ).ask()
