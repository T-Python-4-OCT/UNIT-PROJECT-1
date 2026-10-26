"""The interactive part: questions, menu and actions (Lessons 3, 4, 5, 8)."""
import functools
import math
import sys
from datetime import date

import humanize                      # friendly dates: "today", "in 14 days"
import plotext as plt                # bar charts inside the terminal
from pyfiglet import figlet_format   # big ASCII-art title
from rich.console import Console
from rich.prompt import Confirm, Prompt

from .models import (CATEGORIES, DEFAULT_SPLIT, BudgetError, Expense, Ticket, Trip,
                     TripError, ValidationError)
from .report import build_report, format_money, to_text
from .storage import delete_saved_trip, load_trip, save_report, save_trip

console = Console()

# Lets people type Arabic digits (٠١٢٣) and still get valid numbers.
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩٫", "0123456789.")


# ======================= decorator =======================
def safe_action(func):
    """Decorator: show a friendly message instead of crashing on our own errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TripError as err:
            console.print(f"[red]!! {err}[/]")
            return None
    return wrapper


# ======================= questions =======================
def ask_text(question: str, default: str | None = None) -> str:
    """Keep asking until the answer is not empty."""
    while True:
        answer = Prompt.ask(question, default=default or "", show_default=bool(default)).strip()
        if answer:
            return answer
        console.print("[red]This can't be empty.[/]")


def ask_number(question: str, minimum: float = 0.01) -> float:
    """Keep asking until we get a real number >= minimum."""
    while True:
        raw = Prompt.ask(question).translate(ARABIC_DIGITS).replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            console.print("[red]Please enter a number.[/]")
            continue
        if not math.isfinite(value) or value < minimum:  # blocks nan, inf, negatives
            console.print(f"[red]Enter a number of at least {minimum}.[/]")
            continue
        return value


def ask_date(question: str, default: date | None = None) -> date:
    while True:
        raw = Prompt.ask(f"{question} (YYYY-MM-DD)",
                         default=str(default) if default else "", show_default=bool(default))
        try:
            return date.fromisoformat(raw.translate(ARABIC_DIGITS).strip())
        except ValueError:
            console.print("[red]Use the format YYYY-MM-DD, for example 2026-11-05.[/]")


def ask_choice(question: str, options: list[str]) -> int:
    """Show numbered options and return the index the user picked."""
    for number, option in enumerate(options, start=1):
        console.print(f"  {number}. {option}")
    choices = [str(n) for n in range(1, len(options) + 1)]
    return int(Prompt.ask(question, choices=choices, show_choices=False)) - 1


# ======================= setup =======================
def ask_ticket(trip: Trip) -> None:
    number = ask_text("Ticket number")
    while True:  # ask only the price again if it's too high
        try:
            trip.set_ticket(Ticket(number, ask_number(f"Ticket price in {trip.currency}")))
            return
        except BudgetError as err:
            console.print(f"[red]!! {err} Try again.[/]")


def ask_split(trip: Trip) -> None:
    console.print("Default split: " + ", ".join(f"{k} {v}%" for k, v in DEFAULT_SPLIT.items()))
    if Confirm.ask("Use the default split?", default=True):
        return
    while True:
        split = {cat: int(ask_number(f"  {cat} %", minimum=0)) for cat in CATEGORIES}
        try:
            trip.set_split(split)
            return
        except ValidationError as err:
            console.print(f"[red]!! {err}[/]")


def setup_trip() -> Trip:
    console.rule("New trip")
    destination = ask_text("Where are you going?")
    start = ask_date("Start date", default=date.today())
    end = ask_date("End date")
    while end < start:
        console.print("[red]The end date can't be before the start date.[/]")
        end = ask_date("End date")
    currency = ask_text("Your budget currency", default="SAR").upper()
    local = ask_text("Currency at the destination (e.g. TRY, EUR)", default=currency).upper()
    rate = ask_number(f"Exchange rate: 1 {currency} = ? {local}", 0.0001) if local != currency else 1.0
    budget = ask_number(f"Total budget in {currency}")

    trip = Trip(destination, start, end, budget, currency, local, rate)
    ask_ticket(trip)
    console.print(f"Left after the ticket: [bold]{format_money(trip.trip_budget, currency)}[/]")
    ask_split(trip)
    save_trip(trip)
    console.print("[green]Trip saved. Have a great journey![/]")
    return trip


# ======================= menu actions =======================
@safe_action
def add_expense(trip: Trip) -> None:
    category = CATEGORIES[ask_choice("Category", list(CATEGORIES))]

    paid_local = False
    if trip.uses_foreign_currency():
        paid_local = ask_choice(f"Paid in (1 {trip.currency} = {trip.rate:g} {trip.local_currency})",
                                [trip.local_currency, trip.currency]) == 0
    paid_in = trip.local_currency if paid_local else trip.currency
    amount = ask_number(f"Amount in {paid_in}")
    note = Prompt.ask("Note (optional)", default="", show_default=False)
    day = ask_date("Date", default=date.today())

    if paid_local:
        converted = trip.to_base(amount)
        console.print(f"{amount:,.2f} {paid_in} = {converted:,.2f} {trip.currency}")
        expense = Expense(category, converted, note, day, amount, paid_in, trip.rate)
    else:
        expense = Expense(category, amount, note, day)

    trip.add_expense(expense)
    save_trip(trip)
    remaining = trip.category_status(category)[2]
    if remaining >= 0:
        console.print(f"[green]Saved. {category} has {format_money(remaining, trip.currency)} left.[/]")
    else:
        console.print(f"[yellow]Saved. {category} is over by "
                      f"{format_money(-remaining, trip.currency)}. Use your reserve.[/]")


@safe_action
def delete_expense(trip: Trip) -> None:
    """Made a mistake? Delete it and add it again."""
    if not trip.expenses:
        console.print("No expenses yet.")
        return
    options = [f"{humanize.naturalday(e.day):<10} {e.category:<11} "
               f"{format_money(e.amount, trip.currency):>14}  {e.note}"
               for e in trip.expenses]
    index = ask_choice("Which expense?", options)
    if Confirm.ask("Delete it?"):
        removed = trip.remove_expense(index)
        save_trip(trip)
        console.print(f"[green]Deleted {format_money(removed.amount, trip.currency)}.[/]")


def show_chart(trip: Trip) -> None:
    """Bar chart of the money spent in each category (plotext)."""
    if trip.total_spent == 0:
        return
    # plotext draws Unicode bars; Windows terminals may default to cp1256.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    plt.clear_figure()
    plt.simple_bar([c.capitalize() for c in CATEGORIES],
                   [trip.spent_in(c) for c in CATEGORIES],
                   width=60, title=f"Spent per category ({trip.currency})")
    plt.show()


def show_summary(trip: Trip) -> None:
    console.print(build_report(trip, date.today()))
    show_chart(trip)


@safe_action
def final_report(trip: Trip) -> None:
    report = build_report(trip, date.today(), final=True)
    console.print(report)
    path = save_report(to_text(report), trip.destination)
    console.print(f"[green]Report saved to: {path}[/]")


@safe_action
def add_days(trip: Trip) -> None:
    trip.extend(int(ask_number("How many days do you want to add?", minimum=1)))
    save_trip(trip)
    console.print(f"[green]New end date: {trip.end}[/] ({trip.days_total()} days)")


@safe_action
def cancel_trip(trip: Trip) -> bool:
    """Show the money you keep, save it in a report, delete the trip."""
    if not Confirm.ask("Cancel this trip and delete its data?"):
        return False
    keep = format_money(trip.remaining_total, trip.currency)
    console.print(f"Money you keep: [bold green]{keep}[/]")
    report = to_text(build_report(trip, date.today(), final=True)) + f"\nTrip cancelled. Money you keep: {keep}\n"
    console.print(f"Report saved to: {save_report(report, trip.destination)}")
    delete_saved_trip()
    return True


# ======================= main loop =======================
MENU = {
    "1": ("Add an expense", add_expense),
    "2": ("Delete an expense", delete_expense),
    "3": ("Show summary", show_summary),
    "4": ("Final report", final_report),
    "5": ("Add days to the trip", add_days),
    "6": ("Cancel trip", cancel_trip),
}


def run() -> None:
    banner = figlet_format("Trip Budget", font="small")
    console.print(banner, style="bold cyan", markup=False, highlight=False)
    try:
        trip = load_trip()
    except TripError as err:
        console.print(f"[red]!! {err}[/]")
        return

    if trip is None:
        trip = setup_trip()
    else:
        console.print(f"Welcome back! Trip to [bold]{trip.destination}[/].")

    today = date.today()
    if trip.is_finished(today):
        console.print(f"Your trip ended {humanize.naturaldelta(today - trip.end)} ago. "
                      "Choose 4 to see and save the final report.")
    elif today < trip.start:
        console.print(f"Your trip starts in {humanize.naturaldelta(trip.start - today)}. "
                      "You can already log expenses (choose 1).")
    else:
        while Confirm.ask("Did you spend anything since last time?"):
            add_expense(trip)
    show_summary(trip)

    while True:
        console.print()
        for key, (label, _) in MENU.items():
            console.print(f"  {key}. {label}")
        console.print("  0. Exit")
        choice = Prompt.ask("Choose", choices=["0", *MENU], show_choices=False)
        if choice == "0":
            break
        _, action = MENU[choice]
        if action(trip) is True:  # only "cancel trip" returns True
            break
    console.print("Goodbye!")
