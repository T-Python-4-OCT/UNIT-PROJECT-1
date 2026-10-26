"""Builds the summary and the final report as rich tables."""
import io
from datetime import date, timedelta

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

from .models import CATEGORIES, Trip

# Lambda: format a number as money, e.g. 1800 -> "1,800.00 SAR"
format_money = lambda amount, currency: f"{amount:,.2f} {currency}"


def progress_bar(spent: float, budget: float, width: int = 15) -> str:
    """Text bar like ━━━━━─────── 40%, red when the category is over budget."""
    ratio = min(spent / budget, 1) if budget > 0 else 0
    percent = spent / budget * 100 if budget > 0 else 0
    color = "red" if percent > 100 else "yellow" if percent > 80 else "green"
    filled = int(ratio * width)
    return f"[{color}]{'━' * filled}[/][dim]{'─' * (width - filled)}[/] {percent:.0f}%"


def build_report(trip: Trip, today: date, final: bool = False) -> Group:
    money = lambda value: format_money(value, trip.currency)

    # --- header: budget and ticket ---
    header = (f"{trip.start} → {trip.end}  ({trip.days_total()} days)\n"
              f"Total budget: {money(trip.total_budget)}")
    if trip.ticket:
        header += f"   Ticket {trip.ticket.number}: -{money(trip.ticket.amount)}"
    header += f"\nTrip budget: [bold]{money(trip.trip_budget)}[/]"
    if trip.uses_foreign_currency():
        header += f"   (1 {trip.currency} = {trip.rate:g} {trip.local_currency})"
    title = "FINAL REPORT" if final else "TRIP SUMMARY"
    parts = [Panel(header, title=f"{title}: {trip.destination}", expand=False)]

    # --- one row per category ---
    table = Table(box=box.SQUARE)  # simple lines that every terminal font can draw
    for column in ("Category", "Used", "Spent", "Budget", "Left"):
        table.add_column(column, justify="left" if column in ("Category", "Used") else "right")
    for category in CATEGORIES:
        budget, spent, remaining = trip.category_status(category)  # tuple unpacking
        left = f"[red]{money(remaining)}[/]" if remaining < 0 else money(remaining)
        table.add_row(category.capitalize(), progress_bar(spent, budget),
                      money(spent), money(budget), left)
    parts.append(table)

    # --- totals ---
    lines = [f"Total spent: [bold]{money(trip.total_spent)}[/]",
             f"Total left:  [bold]{money(trip.remaining_total)}[/]"]
    days_left = trip.days_left(today)
    if not final and days_left:
        if trip.remaining_total > 0:
            lines.append(f"Days left: {days_left} (including today) → you can spend about "
                         f"[bold green]{money(trip.daily_allowance(today))}[/] per day")
        else:
            lines.append(f"[red]No budget left - you are over by {money(-trip.remaining_total)}[/]")

    elapsed = trip.days_elapsed(today)
    if elapsed:
        # Sets: all days so far minus the days that have spending
        all_days = {trip.start + timedelta(days=i) for i in range(elapsed)}
        quiet_days = all_days - trip.days_with_spending()
        lines.append(f"Days with no spending logged: {len(quiet_days)} of {elapsed}")
    parts.append("\n".join(lines))

    # --- final report: every expense ---
    if final:
        expenses = Table(title="All expenses", box=box.SQUARE)
        for column in ("Date", "Category", "Amount", "Note"):
            expenses.add_column(column)
        for e in sorted(trip.expenses, key=lambda e: e.day):  # lambda as sort key
            note = e.note
            if e.local_amount:
                note += f"  ({e.local_amount:,.2f} {e.local_currency} @ {e.rate:g})"
            expenses.add_row(str(e.day), e.category, money(e.amount), note)
        parts.append(expenses)
        if trip.remaining_total >= 0:
            parts.append(f"[green]You are UNDER budget with {money(trip.remaining_total)} left.[/]")
        else:
            parts.append(f"[red]You are OVER budget by {money(-trip.remaining_total)}.[/]")

    return Group(*parts)


def to_text(renderable) -> str:
    """Turn a rich table/panel into plain text so it can be saved to a .txt file."""
    console = Console(file=io.StringIO(), width=90, record=True)
    console.print(renderable)
    return console.export_text()
