
"""Riyadh Smart Trip: an interactive command-line trip planner."""
from __future__ import annotations

from datetime import datetime

from rich.align import Align
from rich.box import ROUNDED, DOUBLE
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import questionary

from storage import delete_trip, load_trips, update_trip
from traffic_data import (
    TIME_FORMAT,
    estimate_trip_duration,
    suggest_departure_time,
)
from traffic_stats import display_traffic_report
from transport_advisor import compare_transport_options
from trips import plan_trip

console = Console()

MENU_OPTIONS = [
    ("1", "Plan a Trip"),
    ("2", "View Saved Trips"),
    ("3", "View Trip Report"),
    ("4", "Update a Trip"),
    ("5", "Delete a Trip"),
    ("6", "Suggest Departure Time"),
    ("7", "Exit"),
]

EXIT_CHOICE = "7"
INVALID_TIME_MESSAGE = (
    "Invalid time. Please use HH:MM, for example 08:30."
)


def show_welcome() -> None:
    """Display the project welcome screen."""
    title = Text()
    title.append("RIYADH\n", style="bold cyan")
    title.append("SMART TRIP", style="bold white")

    subtitle = Text(
        "Smart Travel Planner for Riyadh\n"
        "Plan smarter. Travel better.",
        style="bright_white",
        justify="center",
    )

    content = Align.center(
        Text.assemble(title, "\n\n", subtitle)
    )

    console.print()
    console.print(
        Panel(
            content,
            title="[bold green]WELCOME[/bold green]",
            subtitle="[bright_black]SMART MOBILITY CONSOLE[/bright_black]",
            border_style="cyan",
            box=DOUBLE,
            padding=(1, 3),
            expand=True,
        )
    )


def display_menu() -> None:
    """Print the main menu."""
    table = Table(
        title="[bold cyan]MAIN MENU[/bold cyan]",
        caption="[bright_black]Use the arrow keys and press Enter to choose[/bright_black]",
        box=ROUNDED,
        border_style="bright_black",
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )

    table.add_column("Option", justify="center", style="bold yellow")
    table.add_column("Feature", style="white")

    for option, feature in MENU_OPTIONS:
        if option == EXIT_CHOICE:
            table.add_row(
                option,
                "[bold red]Exit[/bold red]",
            )
        else:
            table.add_row(option, feature)

    console.print()
    console.print(table)


def print_trip_list(trips: list[dict]) -> None:
    """Print a numbered list of trips."""
    table = Table(
        title="[bold cyan]YOUR SAVED TRIPS[/bold cyan]",
        box=ROUNDED,
        border_style="bright_black",
        header_style="bold cyan",
        expand=True,
    )

    table.add_column("#", justify="center", style="yellow")
    table.add_column("Origin", style="white")
    table.add_column("Destination", style="white")

    for index, trip in enumerate(trips, start=1):
        table.add_row(
            str(index),
            trip["origin"],
            trip["destination"],
        )

    console.print(table)


def ask_trip_number(prompt: str, trips: list[dict]) -> int | None:
    """Ask for a trip number and return its list index."""
    try:
        number = int(input(prompt))
    except ValueError:
        show_message("Invalid trip number!", "error")
        return None

    if not 1 <= number <= len(trips):
        show_message("Invalid trip number!", "error")
        return None

    return number - 1


def ask_time(prompt: str) -> str | None:
    """Ask for a time in HH:MM format."""
    value = input(prompt).strip()

    try:
        datetime.strptime(value, TIME_FORMAT)
    except ValueError:
        show_message(INVALID_TIME_MESSAGE, "error")
        return None

    return value


def show_message(message: str, message_type: str = "info") -> None:
    """Display a consistent status message."""
    styles = {
        "success": ("green", "SUCCESS"),
        "error": ("red", "ERROR"),
        "warning": ("yellow", "WARNING"),
        "info": ("cyan", "INFO"),
    }

    color, title = styles.get(message_type, styles["info"])

    console.print(
        Panel(
            message,
            title=f"[bold {color}]{title}[/bold {color}]",
            border_style=color,
            box=ROUNDED,
            padding=(0, 2),
            expand=True,
        )
    )


def view_saved_trips() -> None:
    """Print all saved trips."""
    trips = load_trips()

    if not trips:
        show_message("No saved trips found!", "warning")
        return

    table = Table(
        title="[bold cyan]SAVED TRIPS[/bold cyan]",
        box=ROUNDED,
        border_style="bright_black",
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )

    table.add_column("#", justify="center", style="yellow")
    table.add_column("From", style="white")
    table.add_column("To", style="white")
    table.add_column("Departure", justify="center")
    table.add_column("Traffic", justify="center")
    table.add_column("Car (min)", justify="right", style="cyan")
    table.add_column("Metro (min)", justify="right", style="green")

    for index, trip in enumerate(trips, start=1):
        metro_duration = trip.get("metro_duration")

        table.add_row(
            str(index),
            str(trip["origin"]),
            str(trip["destination"]),
            str(trip["departure_time"]),
            str(trip["traffic_period"]),
            str(trip["estimated_minutes"]),
            str(metro_duration) if metro_duration is not None else "N/A",
        )

    console.print(table)


def view_trip_report() -> None:
    """Print the trip report and the traffic report."""
    trips = load_trips()

    console.print()
    console.rule("[bold cyan]TRIP REPORT[/bold cyan]", style="bright_black")

    if not trips:
        show_message(
            "No saved trips available for reporting.",
            "warning",
        )
    else:
        average = (
            sum(trip["estimated_minutes"] for trip in trips)
            / len(trips)
        )
        fastest = min(
            trips,
            key=lambda trip: trip["estimated_minutes"],
        )

        report = Table(
            box=ROUNDED,
            border_style="bright_black",
            show_header=False,
            expand=True,
        )
        report.add_column("Metric", style="cyan")
        report.add_column("Details", style="white")

        report.add_row("Total Saved Trips", str(len(trips)))
        report.add_row("Average Duration", f"{average:.1f} minutes")
        report.add_row(
            "Fastest Car Trip",
            f"{fastest['origin']} -> {fastest['destination']}",
        )
        report.add_row(
            "Fastest Car Duration",
            f"{fastest['estimated_minutes']} minutes",
        )

        metro_trips = [
            trip for trip in trips
            if isinstance(trip.get("metro_duration"), (int, float))
            and trip["metro_duration"] > 0
        ]

        if metro_trips:
            fastest_metro = min(
                metro_trips,
                key=lambda trip: trip["metro_duration"],
            )
            metro_summary = (
                f"{fastest_metro['origin']} -> "
                f"{fastest_metro['destination']} "
                f"({fastest_metro['metro_duration']} minutes)"
            )
        else:
            metro_summary = "No saved metro trip data available yet."

        report.add_row("Fastest Metro Trip", metro_summary)

        console.print(
            Panel(
                report,
                title="[bold green]YOUR TRAVEL SUMMARY[/bold green]",
                border_style="cyan",
                box=ROUNDED,
                padding=1,
            )
        )

    console.rule("[bold cyan]TRAFFIC REPORT[/bold cyan]", style="bright_black")
    display_traffic_report()


def update_saved_trip() -> None:
    """Change the departure time of a saved trip."""
    trips = load_trips()

    if not trips:
        show_message("No saved trips found!", "warning")
        return

    print_trip_list(trips)

    index = ask_trip_number("Enter trip number to update: ", trips)

    if index is None:
        return

    new_time = ask_time("Enter new departure time (HH:MM): ")

    if new_time is None:
        return

    trip = trips[index]
    base_minutes = trip.get("base_minutes")

    if base_minutes is None:
        show_message(
            "Base trip duration is unavailable for this trip.",
            "error",
        )
        return

    period, duration = estimate_trip_duration(base_minutes, new_time)

    updated_trip = {
        "departure_time": new_time,
        "traffic_period": period,
        "estimated_minutes": duration,
        "car_duration": duration,
    }

    result = compare_transport_options(
        trip["origin"],
        trip["destination"],
        new_time,
        interactive=False,
    )

    if result is not None:
        updated_trip.update(result)

    update_trip(index, updated_trip)
    show_message("Trip updated successfully!", "success")


def delete_saved_trip() -> None:
    """Delete a saved trip chosen by the user."""
    trips = load_trips()

    if not trips:
        show_message("No saved trips found!", "warning")
        return

    print_trip_list(trips)

    index = ask_trip_number("Enter trip number to delete: ", trips)

    if index is not None:
        delete_trip(index)
        show_message("Trip deleted successfully!", "success")



def suggest_time() -> None:
    """Suggest a departure time for a saved trip and an arrival time."""
    trips = load_trips()

    if not trips:
        show_message("No saved trips found!", "warning")
        return

    print_trip_list(trips)

    index = ask_trip_number("Choose a trip number: ", trips)

    if index is None:
        return

    arrival_time = ask_time("Enter desired arrival time (HH:MM): ")

    if arrival_time is None:
        return

    base_minutes = trips[index].get("base_minutes")

    if base_minutes is None:
        show_message("Base trip duration is unavailable.", "error")
        return

    suggest_departure_time(base_minutes, arrival_time)


ACTIONS = {
    "1": plan_trip,
    "2": view_saved_trips,
    "3": view_trip_report,
    "4": update_saved_trip,
    "5": delete_saved_trip,
    "6": suggest_time,
}


def run_menu() -> None:
    """Show the menu and run the chosen action until the user exits."""
    while True:
        display_menu()
        choice = questionary.select(
            "Choose an option:",
            choices=[
                questionary.Choice(title=feature, value=option)
                for option, feature in MENU_OPTIONS
            ],
        ).ask()

        if choice is None or choice == EXIT_CHOICE:
            show_message(
                "Thank you for using Riyadh Smart Trip!",
                "success",
            )
            return

        action = ACTIONS.get(choice)

        if action is None:
            show_message(
                "Invalid choice. Please use the arrow keys to select an option.",
                "error",
            )
        else:
            console.print()
            action()
            console.input("\n[bright_black]Press Enter to return to the menu...[/bright_black]")


def main() -> None:
    """Run the application and exit cleanly on Ctrl+C or Ctrl+D."""
    try:
        show_welcome()
        run_menu()
    except (KeyboardInterrupt, EOFError):
        console.print("\n")
        show_message("Goodbye!", "info")


if __name__ == "__main__":
    main()
