from datetime import datetime

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from agency.config import APP_NAME, CURRENCY, DEFAULT_DAYS
from agency.flags import flag
from agency.services import planner
from agency.ui.console import console

STATUS_STYLE = {
    "pending": "yellow",
    "confirmed": "green",
    "completed": "blue",
    "cancelled": "red",
}
CATEGORY_STYLE = {"city": "cyan", "beach": "yellow", "culture": "magenta", "adventure": "green"}

CATEGORY_ICON = {"city": "🌆", "beach": "🌴", "culture": "🏺", "adventure": "🧭"}


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


def category_label(category: str) -> str:
    color = CATEGORY_STYLE.get(category, "white")
    return f"{CATEGORY_ICON.get(category, '🌍')} [{color}]{category}[/]"


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
                      category_label(destination.category), money(destination.flight), money(destination.hotel),
                      escape(destination.best_season), style="strike dim" if destination.suspended else None)
    console.print(table)


def show_country_detail(destination, days: int = DEFAULT_DAYS) -> None:
    sample = planner.estimate(destination, days, 1, "standard")
    lines = [
        f"[bold]{place(destination)}[/bold]  "
        f"({category_label(destination.category)})",
        f"Best season: [yellow]{escape(destination.best_season)}[/yellow]",
        "",
        "[bold]Highlights[/bold]",
        *[f"  • {escape(h)}" for h in destination.highlights],
        "",
        "[bold]Daily costs per person[/bold]",
        f"  Hotel {money(destination.hotel)}/night  |  Food {money(destination.food)}  |  "
        f"Transport {money(destination.transport)}  |  Activities {money(destination.activities)}",
        "",
        f"Example: {days} days, 1 traveler, standard style = [bold green]{money(sample['Total'])}[/]",
    ]
    if destination.suspended:
        lines += ["", "[bold red]This trip is suspended until further notice and cannot be booked.[/]"]
    console.print(Panel("\n".join(lines), title=f"Destination #{destination.id}",
                        border_style="cyan", expand=False))


def temperature_style(celsius: float) -> str:
    if celsius >= 35:
        return "bold red"
    if celsius >= 25:
        return "yellow"
    if celsius >= 15:
        return "green"
    return "cyan"


def show_weather(report: dict) -> None:
    temp = report["temperature"]
    header = (f"[bold]Now in {escape(report['city'])}:[/bold] "
              f"[{temperature_style(temp)}]{temp}°C[/]  |  {report['condition']}  |  "
              f"wind {report['wind']} km/h")
    table = Table(title="Forecast", header_style="bold magenta", border_style="cyan")
    table.add_column("Date")
    table.add_column("Conditions")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")
    for day in report["days"]:
        table.add_row(day["date"], day["condition"],
                      f"[{temperature_style(day['min'])}]{day['min']}°C[/]",
                      f"[{temperature_style(day['max'])}]{day['max']}°C[/]")
    console.print(Panel(header, title="Live weather", border_style="green", expand=False))
    console.print(table)


def show_plan_options(matches, budget: int) -> None:
    table = Table(title=f"Trips within {money(budget)}", header_style="bold magenta", border_style="cyan")
    for column, style in [("#", "cyan"), ("City details", ""), ("Type", ""), ("Total", "green"), ("Left", "yellow")]:
        table.add_column(column, style=style, no_wrap=column in ("Total", "Left"))
    for number, (destination, cost) in enumerate(matches, start=1):
        details = (f"{flag(destination.country)} [bold]{escape(destination.city)}[/bold], {escape(destination.country)}\n"
                   f"[dim]Best season: {escape(destination.best_season)}\n"
                   f"Highlights: {escape(', '.join(destination.highlights[:3]))}[/dim]")
        table.add_row(str(number), details, category_label(destination.category),
                      money(cost["Total"]), money(budget - cost["Total"]), end_section=True)
    console.print(table)


def show_breakdown(cost: dict, budget=None, title="Cost breakdown") -> None:
    table = Table(title=title, header_style="bold magenta", border_style="cyan")
    table.add_column("Item")
    table.add_column("Cost", justify="right")
    for item, value in cost.items():
        if item == "Total":
            table.add_section()
            table.add_row("[bold]Total[/bold]", f"[bold green]{money(value)}[/]")
        elif value < 0:
            table.add_row(f"[green]{escape(item)}[/green]", f"[green]{money(value)}[/green]")
        else:
            table.add_row(item, money(value))
    if budget is not None:
        left = budget - cost["Total"]
        style = "green" if left >= 0 else "red"
        table.add_row("Remaining budget", f"[{style}]{money(left)}[/]")
    console.print(table)


def show_itinerary(destination, days: int) -> None:
    lines = [f"[cyan]Day {i}[/cyan]: {escape(step)}"
             for i, step in enumerate(planner.build_itinerary(destination, days), start=1)]
    title = f"{place(destination)} - {days} days"
    console.print(Panel("\n".join(lines), title=title, border_style="cyan", expand=False))
