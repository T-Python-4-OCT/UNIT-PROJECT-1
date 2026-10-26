"""Riyadh Smart Trip: an interactive command-line trip planner."""
from __future__ import annotations

from datetime import datetime

from rich.console import Console
from rich.table import Table

from storage import delete_trip, load_trips, save_trip, update_trip
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
    ("6", "Compare Transport Options"),
    ("7", "Suggest Departure Time"),
    ("8", "Exit"),
]
EXIT_CHOICE = "8"
INVALID_TIME_MESSAGE = "Invalid time. Please use HH:MM, for example 08:30."


def display_menu() -> None:
    """Print the main menu."""
    table = Table(title="Riyadh Smart Trip", header_style="bold cyan")

    table.add_column("Option", justify="center", style="yellow")
    table.add_column("Feature", style="green")

    for option, feature in MENU_OPTIONS:
        table.add_row(option, feature)

    console.print(table)


def print_trip_list(trips: list[dict]) -> None:
    """Print a numbered list of trips."""
    for index, trip in enumerate(trips, start=1):
        print(f"{index}. {trip['origin']} -> {trip['destination']}")


def ask_trip_number(prompt: str, trips: list[dict]) -> int | None:
    """Ask for a trip number and return its list index.

    Returns:
        The zero-based index, or None if the input is invalid.
    """
    try:
        number = int(input(prompt))
    except ValueError:
        print("Invalid trip number!")
        return None

    if not 1 <= number <= len(trips):
        print("Invalid trip number!")
        return None

    return number - 1


def ask_time(prompt: str) -> str | None:
    """Ask for a time in HH:MM format. Return None if it is invalid."""
    value = input(prompt).strip()

    try:
        datetime.strptime(value, TIME_FORMAT)
    except ValueError:
        print(INVALID_TIME_MESSAGE)
        return None

    return value


def view_saved_trips() -> None:
    """Print all saved trips."""
    trips = load_trips()

    print("\n" + "=" * 46)
    print("             SAVED TRIPS")
    print("=" * 46)

    if not trips:
        print("  No saved trips found!")

    for index, trip in enumerate(trips, start=1):
        print(f"\n  TRIP #{index}")
        print("  " + "-" * 42)
        print(f"  From       : {trip['origin']}")
        print(f"  To         : {trip['destination']}")
        print(f"  Departure  : {trip['departure_time']}")
        print(f"  Traffic    : {trip['traffic_period']}")
        print(f"  Car        : {trip['estimated_minutes']} minutes")

        if trip.get("metro_duration") is not None:
            print(
                f"  Metro      : {trip['metro_duration']} minutes "
                f"({trip.get('metro_line')})"
            )

    print("=" * 46)


def view_trip_report() -> None:
    """Print the trip report and the traffic report."""
    trips = load_trips()

    print("\n" + "=" * 46)
    print("              TRIP REPORT")
    print("=" * 46)

    if not trips:
        print("  No saved trips available for reporting.")
    else:
        average = sum(trip["estimated_minutes"] for trip in trips) / len(trips)
        fastest = min(trips, key=lambda trip: trip["estimated_minutes"])

        print(f"  Total Saved Trips : {len(trips)}")
        print(f"  Average Duration  : {average:.1f} minutes")

        print("\n  FASTEST CAR TRIP")
        print(f"  {fastest['origin']} -> {fastest['destination']}")
        print(f"  {fastest['estimated_minutes']} minutes")

        metro_trips = [
            trip for trip in trips
            if isinstance(trip.get("metro_duration"), (int, float))
            and trip["metro_duration"] > 0
        ]

        print("\n  FASTEST METRO TRIP")

        if metro_trips:
            fastest_metro = min(
                metro_trips, key=lambda trip: trip["metro_duration"]
            )
            print(
                f"  {fastest_metro['origin']} -> "
                f"{fastest_metro['destination']}"
            )
            print(f"  {fastest_metro['metro_duration']} minutes")
        else:
            print("  No saved metro trip data available yet.")

    print("=" * 46)
    display_traffic_report()


def update_saved_trip() -> None:
    """Change the departure time of a saved trip."""
    trips = load_trips()

    if not trips:
        print("\nNo saved trips found!")
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
        print("Base trip duration is unavailable for this trip.")
        return

    period, duration = estimate_trip_duration(base_minutes, new_time)

    updated_trip = {
        "departure_time": new_time,
        "traffic_period": period,
        "estimated_minutes": duration,
        "car_duration": duration,
    }

    result = compare_transport_options(
        trip["origin"], trip["destination"], new_time, interactive=False
    )

    if result is not None:
        updated_trip.update(result)

    update_trip(index, updated_trip)


def delete_saved_trip() -> None:
    """Delete a saved trip chosen by the user."""
    trips = load_trips()

    if not trips:
        print("\nNo saved trips found!")
        return

    print_trip_list(trips)

    index = ask_trip_number("Enter trip number to delete: ", trips)

    if index is not None:
        delete_trip(index)


def compare_options() -> None:
    """Compare car and metro for locations entered by the user."""
    origin = input("Enter starting location: ").strip()
    destination = input("Enter destination: ").strip()
    departure_time = input("Enter departure time (HH:MM): ").strip()

    if not origin or not destination:
        print("\nError: Locations cannot be empty.")
        return

    try:
        datetime.strptime(departure_time, TIME_FORMAT)
    except ValueError:
        print(f"\n{INVALID_TIME_MESSAGE}")
        return

    result = compare_transport_options(origin, destination, departure_time)

    if result is not None:
        save_trip(result)
        print("Trip comparison saved successfully.")


def suggest_time() -> None:
    """Suggest a departure time for a saved trip and an arrival time."""
    trips = load_trips()

    if not trips:
        print("\nNo saved trips found!")
        return

    print("\nSAVED TRIPS")
    print("-" * 42)
    print_trip_list(trips)

    index = ask_trip_number("Choose a trip number: ", trips)

    if index is None:
        return

    arrival_time = ask_time("Enter desired arrival time (HH:MM): ")

    if arrival_time is None:
        return

    base_minutes = trips[index].get("base_minutes")

    if base_minutes is None:
        print("Base trip duration is unavailable.")
        return

    suggest_departure_time(base_minutes, arrival_time)


ACTIONS = {
    "1": plan_trip,
    "2": view_saved_trips,
    "3": view_trip_report,
    "4": update_saved_trip,
    "5": delete_saved_trip,
    "6": compare_options,
    "7": suggest_time,
}


def run_menu() -> None:
    """Show the menu and run the chosen action until the user exits."""
    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == EXIT_CHOICE:
            print("\nThank you for using Riyadh Smart Trip!")
            return

        action = ACTIONS.get(choice)

        if action is None:
            print("\nInvalid choice. Please enter a number from 1 to 8.")
        else:
            action()


def main() -> None:
    """Run the application and exit cleanly on Ctrl+C or Ctrl+D."""
    try:
        run_menu()
    except (KeyboardInterrupt, EOFError):
        print("\n\nGoodbye!")


if __name__ == "__main__":
    main()
