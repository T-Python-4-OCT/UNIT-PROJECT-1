from datetime import datetime

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from agency.config import APP_NAME, CURRENCY
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
    table = Table(title=escape(title), header_style="bold magenta", border_style=border_style)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Action")
    for key, label in items:
        table.add_row(key, f"[red]{label}[/red]" if key == "0" else label)
    console.print(table)
    console.print("[dim]Tip: type b at any question to go back[/dim]")


def place(item) -> str:
    return f"{flag(item.country)} {escape(item.city)}, {escape(item.country)}"


def money(value) -> str:
    return f"{value:,.0f} {CURRENCY}"


def status_text(status: str) -> str:
    return f"[{STATUS_STYLE.get(status, 'white')}]{status}[/]"


def show_welcome(user, notes) -> None:
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    intro = "Here is your agency overview." if user.role == "manager" else "Ready to plan your next trip?"
    lines = [f"[bold]{greeting}, {escape(user.full_name)}![/bold]  Welcome to {APP_NAME}.", intro]
    if user.role == "customer":
        lines.append(f"[cyan]Customer ID: #{user.id}[/cyan]  |  {escape(user.username)}  |  {escape(user.email)}")
    lines += [f"• {escape(note)}" for note in notes]
    console.print(Panel("\n".join(lines), title="Welcome ✈️", border_style="green", expand=False))


def show_countries(items, title="Destinations") -> None:
    table = Table(title=title, header_style="bold magenta", border_style="cyan")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Country", style="bold", no_wrap=True)
    table.add_column("City")
    table.add_column("Type", no_wrap=True)
    table.add_column("Flight", justify="right", style="green", no_wrap=True)
    table.add_column("Hotel/night", justify="right", style="green", no_wrap=True)
    table.add_column("Best season")
    for destination in items:
        city = escape(destination.city) + (" [red](suspended)[/]" if destination.suspended else "")
        table.add_row(str(destination.id), f"{flag(destination.country)} {escape(destination.country)}", city,
                      f"[{CATEGORY_STYLE.get(destination.category, 'white')}]{destination.category}[/]", money(destination.flight), money(destination.hotel),
                      escape(destination.best_season), style="strike dim" if destination.suspended else None)
    console.print(table)
