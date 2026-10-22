"""Pure display functions: they print tables and panels, nothing else."""

from rich.markup import escape
from rich.table import Table

from agency.config import CURRENCY
from agency.flags import flag
from agency.ui.console import console

STATUS_STYLE = {
    "pending": "yellow",
    "confirmed": "green",
    "completed": "blue",
    "cancelled": "red",
}
CATEGORY_STYLE = {"city": "cyan", "beach": "yellow", "culture": "magenta", "adventure": "green"}


def show_menu(title: str, items, border_style: str = "cyan") -> None:
    """Draw a numbered menu. `items` is a list of (key, label); key "0" is shown in red."""
    table = Table(title=escape(title), header_style="bold magenta", border_style=border_style)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Action")
    for key, label in items:
        table.add_row(key, f"[red]{label}[/red]" if key == "0" else label)
    console.print(table)
    console.print("[dim]Tip: type b at any question to go back[/dim]")


def place(item) -> str:
    """"🇹🇷 Istanbul, Turkey" for a destination or a booking (anything with a city and a country)."""
    return f"{flag(item.country)} {escape(item.city)}, {escape(item.country)}"


def money(value) -> str:
    """Format a number as money, e.g. 1,200 SAR."""
    return f"{value:,.0f} {CURRENCY}"


def status_text(status: str) -> str:
    """A booking status wrapped in its color."""
    return f"[{STATUS_STYLE.get(status, 'white')}]{status}[/]"


def show_countries(items, title="Destinations") -> None:
    """Table of destinations. Suspended ones are struck through."""
    table = Table(title=title, header_style="bold magenta", border_style="cyan")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Country", style="bold", no_wrap=True)
    table.add_column("City")
    table.add_column("Type")
    table.add_column("Flight", justify="right", style="green")
    table.add_column("Hotel/night", justify="right", style="green")
    table.add_column("Best season")
    for destination in items:
        color = CATEGORY_STYLE.get(destination.category, "white")
        city = escape(destination.city) + (" [red](suspended)[/]" if destination.suspended else "")
        table.add_row(str(destination.id), f"{flag(destination.country)} {escape(destination.country)}", city,
                      f"[{color}]{destination.category}[/]", money(destination.flight), money(destination.hotel),
                      escape(destination.best_season), style="strike dim" if destination.suspended else None)
    console.print(table)
