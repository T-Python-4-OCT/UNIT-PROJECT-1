
"""Compare car and metro options for a trip and recommend one."""
from __future__ import annotations

import json

import questionary
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from metro_data import estimate_metro_route_duration, find_metro_route
from traffic_data import estimate_trip_duration
from trip_charts import show_transport_chart

console = Console()

ROUTES_FILE = "routes.json"
FUEL_PRICE_SAR = 2.18
FUEL_CONSUMPTION_PER_100_KM = 6
METRO_COST_SAR = 4

PRIORITY_CHOICES = {
    "Fastest Trip": "fastest",
    "Lowest Cost": "cheapest",
    "Best Balance (Time + Cost)": "balanced",
}


def choose_trip_priority() -> str | None:
    """Ask the user for a trip priority."""
    choice = questionary.select(
        "Choose your trip priority:",
        choices=list(PRIORITY_CHOICES),
    ).ask()

    return PRIORITY_CHOICES.get(choice)


def load_routes(routes_file: str = ROUTES_FILE) -> list[dict]:
    """Load the sample car routes."""
    with open(routes_file, "r", encoding="utf-8") as file:
        return json.load(file)["routes"]


def normalize_location(location: str) -> str:
    """Normalize a location name so spelling variants match."""
    return location.strip().lower().replace("oo", "u").replace(" ", "")


def find_transport_options(origin: str, destination: str) -> dict | None:
    """Find the sample route between two locations, or None."""
    origin = normalize_location(origin)
    destination = normalize_location(destination)

    for route in load_routes():
        if (
            normalize_location(route["origin"]) == origin
            and normalize_location(route["destination"]) == destination
        ):
            return route

    return None


def calculate_car_fuel_cost(distance_km):
    if distance_km is None:
        return None

    if not isinstance(distance_km, (int, float)) or isinstance(distance_km, bool):
        return None

    if distance_km <= 0:
        return None

    fuel_cost = (
        distance_km
        * FUEL_CONSUMPTION_PER_100_KM
        / 100
        * FUEL_PRICE_SAR
    )

    return round(fuel_cost, 2)


def get_recommendation(
    priority: str | None,
    car_duration: int,
    car_cost: float | None,
    metro_duration: int,
    metro_cost: float,
) -> tuple[str | None, str]:
    """Recommend car or metro for the chosen priority."""
    if priority == "fastest":
        recommended = "Car" if car_duration <= metro_duration else "Metro"
        return recommended, "It has the shorter estimated travel time."

    if priority == "cheapest":
        if car_cost is None:
            return None, "The car cost cannot be calculated."

        recommended = "Car" if car_cost <= metro_cost else "Metro"
        return recommended, "It has the lower estimated cost."

    if car_cost is None:
        return None, (
            "The car cost is unavailable, so a balanced "
            "comparison cannot be made."
        )

    longest_time = max(car_duration, metro_duration)
    highest_cost = max(car_cost, metro_cost)

    car_score = car_duration / longest_time + car_cost / highest_cost
    metro_score = metro_duration / longest_time + metro_cost / highest_cost

    recommended = "Car" if car_score <= metro_score else "Metro"
    return recommended, "It has the lower combined time-and-cost score."


def display_smart_trip_summary(
    origin: str,
    destination: str,
    car_duration: int,
    car_cost: float | None,
    metro_duration: int,
    metro_cost: float,
    priority: str | None,
) -> str | None:
    """Display time/cost differences and the recommendation."""
    table = Table(
        title="[bold cyan]SMART TRIP SUMMARY[/bold cyan]",
        box=ROUNDED,
        border_style="bright_black",
        header_style="bold cyan",
        expand=True,
    )
    table.add_column("Metric", style="white")
    table.add_column("Result", style="cyan")

    table.add_row("Route", f"{origin} → {destination}")

    time_difference = abs(car_duration - metro_duration)

    if car_duration < metro_duration:
        time_result = f"Car is {time_difference} minutes faster"
    elif metro_duration < car_duration:
        time_result = f"Metro is {time_difference} minutes faster"
    else:
        time_result = "Both options take the same time"

    table.add_row("Time Advantage", time_result)

    if car_cost is None:
        cost_result = "Car cost unavailable"
    else:
        cost_difference = abs(car_cost - metro_cost)

        if car_cost < metro_cost:
            cost_result = f"Car saves {cost_difference:.2f} SAR"
        elif metro_cost < car_cost:
            cost_result = f"Metro saves {cost_difference:.2f} SAR"
        else:
            cost_result = "Both options cost the same"

    table.add_row("Cost Advantage", cost_result)

    recommended, reason = get_recommendation(
        priority, car_duration, car_cost, metro_duration, metro_cost
    )

    console.print(table)

    if recommended is None:
        console.print(
            Panel(
                reason,
                title="[bold yellow]Recommendation Unavailable[/bold yellow]",
                border_style="yellow",
                box=ROUNDED,
            )
        )
    else:
        console.print(
            Panel(
                f"[bold green]Recommended option: {recommended}[/bold green]\n"
                f"{reason}",
                title="[bold green]YOUR RECOMMENDATION[/bold green]",
                border_style="green",
                box=ROUNDED,
                padding=(1, 2),
            )
        )

    return recommended


def _print_car_section(
    car_duration: int, car_cost: float | None, period: str
) -> None:
    """Display car details in a formatted panel."""
    table = Table(show_header=False, box=None, expand=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Duration", f"{car_duration} minutes")
    table.add_row(
        "Estimated Fuel Cost",
        f"{car_cost:.2f} SAR" if car_cost is not None
        else "Distance unavailable",
    )
    table.add_row("Traffic Period", period)

    console.print(
        Panel(
            table,
            title="[bold cyan]CAR[/bold cyan]",
            border_style="cyan",
            box=ROUNDED,
        )
    )


def _print_metro_unavailable() -> None:
    """Display a clear message when no metro route was found."""
    console.print(
        Panel(
            "[bold yellow]Metro route unavailable[/bold yellow]\n\n"
            "The station names may not be recognized, or the stations "
            "may be on different metro lines.\n\n"
            "[white]The car estimate is still available.[/white]",
            title="[yellow]METRO[/yellow]",
            border_style="yellow",
            box=ROUNDED,
            padding=(1, 2),
        )
    )



def compare_transport_options(
    origin: str,
    destination: str,
    departure_time: str,
    interactive: bool = True,
) -> dict | None:
    """Compare car and metro and return the data to save."""
    route = find_transport_options(origin, destination)

    if route is None:
        console.print(
            Panel(
                "Transport comparison is not available for this route yet.",
                title="[bold yellow]Route Unavailable[/bold yellow]",
                border_style="yellow",
                box=ROUNDED,
            )
        )
        return None

    distance_km = route.get("distance_km")
    base_minutes = route.get("base_duration_minutes")

    if (
        not isinstance(base_minutes, (int, float))
        or isinstance(base_minutes, bool)
        or base_minutes <= 0
    ):
        console.print(
            Panel(
                "Invalid route duration in the sample data.",
                title="[bold red]Data Error[/bold red]",
                border_style="red",
                box=ROUNDED,
            )
        )
        return None

    if distance_km is not None and (
        not isinstance(distance_km, (int, float))
        or isinstance(distance_km, bool)
        or distance_km <= 0
    ):
        distance_km = None

    period, car_duration = estimate_trip_duration(
        base_minutes, departure_time
    )

    car_cost = calculate_car_fuel_cost(distance_km)

    metro_route = find_metro_route(origin, destination)
    metro_duration = None

    if metro_route is not None:
        metro_duration = estimate_metro_route_duration(metro_route)

    if (
        not isinstance(metro_duration, (int, float))
        or isinstance(metro_duration, bool)
        or metro_duration <= 0
    ):
        metro_duration = None

    details = Table(
        show_header=False,
        box=None,
        expand=True,
    )
    details.add_column("Metric", style="cyan")
    details.add_column("Value", style="white")

    details.add_row("From", origin)
    details.add_row("To", destination)
    details.add_row("Departure", departure_time)

    distance_text = (
        f"{distance_km} km"
        if distance_km is not None
        else "Not available"
    )
    details.add_row("Distance", distance_text)

    console.print()
    console.print(
        Panel(
            details,
            title="[bold cyan]TRANSPORT COMPARISON[/bold cyan]",
            border_style="cyan",
            box=ROUNDED,
            padding=(1, 2),
        )
    )

    _print_car_section(car_duration, car_cost, period)

    if metro_route is not None and metro_duration is not None:
        metro_table = Table(
            show_header=False,
            box=None,
            expand=True,
        )
        metro_table.add_column("Metric", style="cyan")
        metro_table.add_column("Value", style="white")

        metro_table.add_row("Line", metro_route["metro_line"])
        metro_table.add_row(
            "Stations",
            str(metro_route["number_of_stations"]),
        )
        metro_table.add_row(
            "Estimated Duration",
            f"About {metro_duration} minutes",
        )
        metro_table.add_row(
            "Estimated Cost",
            f"{METRO_COST_SAR:.2f} SAR",
        )

        console.print(
            Panel(
                metro_table,
                title="[bold green]METRO[/bold green]",
                subtitle="[bright_black]Includes estimated waiting time[/bright_black]",
                border_style="green",
                box=ROUNDED,
            )
        )

        if interactive:
            console.print()
            priority = choose_trip_priority()

            if priority is not None:
                display_smart_trip_summary(
                    origin,
                    destination,
                    car_duration,
                    car_cost,
                    metro_duration,
                    METRO_COST_SAR,
                    priority,
                )

            show_transport_chart(
                car_duration,
                metro_duration,
                origin,
                destination,
            )
    else:
        _print_metro_unavailable()

    return {
        "origin": origin,
        "destination": destination,
        "departure_time": departure_time,
        "base_minutes": base_minutes,
        "estimated_minutes": car_duration,
        "distance_km": distance_km,
        "car_duration": car_duration,
        "car_cost": car_cost,
        "metro_duration": metro_duration,
        "metro_cost": (
            METRO_COST_SAR
            if metro_duration is not None
            else None
        ),
        "metro_line": (
            metro_route["metro_line"]
            if metro_route is not None and metro_duration is not None
            else None
        ),
        "traffic_period": period,
    }
