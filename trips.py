
"""Plan a new trip."""
from __future__ import annotations

from datetime import datetime

from rich.box import ROUNDED
from rich.panel import Panel
from rich.table import Table

from models import Trip
from storage import save_trip
from traffic_data import TIME_FORMAT, estimate_trip_duration
from transport_advisor import (
    compare_transport_options,
    find_transport_options,
)
from rich.console import Console

console = Console()


def plan_trip() -> Trip | None:
    """Ask for trip details, show the trip and comparison, and save it."""

    console.print()
    console.print(
        Panel(
            "[bold cyan]Plan a Trip[/bold cyan]\n"
            "[white]Enter your journey details below.[/white]",
            border_style="cyan",
            box=ROUNDED,
            padding=(1, 2),
        )
    )

    origin = input("Starting location: ").strip()
    destination = input("Destination: ").strip()

    if not origin or not destination:
        console.print(
            Panel(
                "[bold red]Locations cannot be empty.[/bold red]\n"
                "Please enter both a starting location and a destination.",
                title="Input Error",
                border_style="red",
                box=ROUNDED,
            )
        )
        return None

    departure_time = input("Departure time (HH:MM): ").strip()

    try:
        datetime.strptime(departure_time, TIME_FORMAT)
    except ValueError:
        console.print(
            Panel(
                "[bold red]Invalid time.[/bold red]\n"
                "Please use HH:MM, for example 08:30.",
                title="Input Error",
                border_style="red",
                box=ROUNDED,
            )
        )
        return None

    route = find_transport_options(origin, destination)

    if route is None:
        console.print(
            Panel(
                "Sorry, this route is not available in our sample data.\n"
                "Please check the location names and try again.",
                title="[bold yellow]Route Unavailable[/bold yellow]",
                border_style="yellow",
                box=ROUNDED,
            )
        )
        return None

    base_minutes = route["base_duration_minutes"]
    period, estimated_minutes = estimate_trip_duration(
        base_minutes, departure_time
    )

    trip = Trip(
        origin,
        destination,
        departure_time,
        base_minutes,
        period,
        estimated_minutes,
    )

    summary = Table(
        box=ROUNDED,
        show_header=False,
        border_style="cyan",
        expand=True,
    )
    summary.add_column("Field", style="bold cyan", width=22)
    summary.add_column("Details", style="white")

    summary.add_row("Starting Location", trip.origin)
    summary.add_row("Destination", trip.destination)
    summary.add_row("Departure Time", trip.departure_time)
    summary.add_row("Traffic Period", period)
    summary.add_row("Estimated Duration", f"{estimated_minutes} minutes")

    console.print(
        Panel(
            summary,
            title="[bold cyan]TRIP SUMMARY[/bold cyan]",
            border_style="cyan",
            box=ROUNDED,
            padding=(1, 2),
        )
    )

    trip_data = trip.to_dict()

    # Add car/metro comparison data to the saved trip when available.
    result = compare_transport_options(
        trip.origin, trip.destination, trip.departure_time
    )

    if result is not None:
        trip_data.update(result)

    save_trip(trip_data)

    console.print(
        Panel(
            "[bold green]✓ Trip saved successfully![/bold green]",
            border_style="green",
            box=ROUNDED,
            padding=(0, 2),
        )
    )

    return trip
