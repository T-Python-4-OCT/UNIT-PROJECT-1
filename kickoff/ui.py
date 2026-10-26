import re
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def info(message):
    console.print(message)


def ok(message):
    console.print(f"[bold green]OK:[/bold green] {message}")


def warn(message):
    console.print(f"[bold yellow]Note:[/bold yellow] {message}")


errors_shown = 0          


def error(message: str) -> None:
    global errors_shown
    errors_shown += 1
    console.print(f"[bold red]Error:[/bold red] {message}")


def title(text):
    console.print()
    console.print(Panel(Text(text, justify="center", style="bold"), style="cyan"))


def ask_text(prompt: str, min_len: int = 1, allow_empty: bool = False) -> str:
    while True:
        value = input(f"{prompt}: ").strip()
        if not value and allow_empty:
            return ""
        if len(value) >= min_len:
            return value
        error(f"Please type at least {min_len} characters.")


def ask_name(prompt: str = "Your full name") -> str:
    
    while True:
        value = " ".join(input(f"{prompt}: ").split())
        if len(value) >= 3 and " " in value and all(ch.isalpha() or ch == " " for ch in value):
            return value
        error("Please type your full name (first and last name, letters only).")


def ask_int(prompt: str, low: int, high: int) -> int:
    """Recursion: if the answer is not valid, the function calls itself again."""
    value = input(f"{prompt}: ").strip()
    if value.isdigit() and low <= int(value) <= high:
        return int(value)
    error(f"Please type a number between {low} and {high}.")
    return ask_int(prompt, low, high)


def ask_phone(prompt: str = "Phone (05XXXXXXXX)") -> str:
    while True:
        value = input(f"{prompt}: ").strip()
        if re.fullmatch(r"05\d{8}", value):
            return value
        error("Phone must look like 05XXXXXXXX.")


def ask_date(prompt: str = "Date (YYYY-MM-DD)") -> str:
    while True:
        value = input(f"{prompt}: ").strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            error("Date must look like 2026-10-27.")
        else:
            return value


def confirm(prompt: str) -> bool:
    while True:
        value = input(f"{prompt} (y/n): ").strip().lower()
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        error("Please type y or n.")


def menu(heading: str, options: dict[int, str]) -> int:
    """options: dict {number: label}. Returns the chosen number (0 is always 'back / exit')."""
    title(heading)
    for number, label in options.items():
        console.print(f"  [bold cyan]{number}[/bold cyan]) {label}")
    return ask_int("Choose", 0, max(options))


def matches_table(session, matches, heading="Matches"):
    """Rows are numbered 1, 2, 3... so the user can type a row number to pick a match."""
    table = Table(title=heading, header_style="bold white on blue")
    table.add_column("#", justify="right", no_wrap=True)
    table.add_column("Date and time", no_wrap=True)
    table.add_column("Match")
    table.add_column("Stadium (city)")
    table.add_column("Status")
    table.add_column("Free", justify="right")
    for number, m in enumerate(matches, start=1):
        if m.status == "finished":
            status = f"[green]{m.home_goals}-{m.away_goals}[/green]"
        else:
            status = "[yellow]Upcoming[/yellow]"
        free = str(session.free_seats(m)) if m.is_open else "-"
        table.add_row(str(number), f"{m.date} {m.time}", session.match_title(m),
                      f"{m.stadium} ({m.city})", status, free)
    console.print(table)


def standings_table(session, rows, heading="Roshn Saudi League standings"):
    total = len(session.teams)
    table = Table(title=heading, header_style="bold white on blue")
    table.add_column("#", justify="right")
    table.add_column("Team")
    for column in ("P", "W", "D", "L", "GF", "GA", "GD", "Pts"):
        table.add_column(column, justify="right")
    for team, position in rows:
        style = None
        if position <= 3:
            style = "green"
        elif position > total - 3:
            style = "bold red"
        gd = f"{team.goal_diff:+d}"
        table.add_row(str(position), team.name_en, str(team.played), str(team.won), str(team.drawn),
                      str(team.lost), str(team.gf), str(team.ga), gd, str(team.points), style=style)
    console.print(table)
    console.print("[green]Green[/green] = top 3   [red]Red[/red] = relegation zone (bottom 3)")