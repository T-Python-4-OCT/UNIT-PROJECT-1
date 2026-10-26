"""Compare car and metro options for a trip and recommend one."""
from __future__ import annotations

import json

import questionary

from metro_data import estimate_metro_route_duration, find_metro_route
from traffic_data import estimate_trip_duration
from trip_charts import show_transport_chart

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
    """Ask the user for a trip priority.

    Returns:
        ``"fastest"``, ``"cheapest"``, ``"balanced"``, or None if the
        prompt was cancelled.
    """
    choice = questionary.select(
        "Choose your trip priority:", choices=list(PRIORITY_CHOICES)
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


def calculate_car_fuel_cost(distance_km: float | None) -> float | None:
    """Estimate the fuel cost in SAR, or None if the distance is invalid."""
    if distance_km is None or distance_km <= 0:
        return None

    fuel_liters = distance_km * FUEL_CONSUMPTION_PER_100_KM / 100
    return round(fuel_liters * FUEL_PRICE_SAR, 2)


def get_recommendation(
    priority: str | None,
    car_duration: int,
    car_cost: float | None,
    metro_duration: int,
    metro_cost: float,
) -> tuple[str | None, str]:
    """Recommend car or metro for the chosen priority.

    Any priority other than ``"fastest"`` or ``"cheapest"`` is treated
    as ``"balanced"``.

    Returns:
        A tuple of (recommended option or None, reason).
    """
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
    """Print the time and cost differences and the recommendation.

    Returns:
        The recommended option, or None if there is no recommendation.
    """
    print("\n" + "=" * 42)
    print("          SMART TRIP SUMMARY")
    print("=" * 42)
    print(f"  Route: {origin} -> {destination}")

    time_difference = abs(car_duration - metro_duration)

    if car_duration < metro_duration:
        print(f"  Time advantage: Car is {time_difference} minutes faster.")
    elif metro_duration < car_duration:
        print(f"  Time advantage: Metro is {time_difference} minutes faster.")
    else:
        print("  Time advantage: Both options take the same time.")

    if car_cost is None:
        print("  Cost comparison unavailable: car distance is missing.")
    else:
        cost_difference = abs(car_cost - metro_cost)

        if car_cost < metro_cost:
            print(f"  Cost advantage: Car saves {cost_difference:.2f} SAR.")
        elif metro_cost < car_cost:
            print(f"  Cost advantage: Metro saves {cost_difference:.2f} SAR.")
        else:
            print("  Cost advantage: Both options cost the same.")

    recommended, reason = get_recommendation(
        priority, car_duration, car_cost, metro_duration, metro_cost
    )

    print("\n  YOUR RECOMMENDATION")

    if recommended is None:
        print("  No recommendation available.")
    else:
        print(f"  Recommended option: {recommended}")
        print(f"  Reason: {reason}")

    print("=" * 42)
    return recommended


def _print_car_section(
    car_duration: int, car_cost: float | None, period: str
) -> None:
    """Print the car part of the comparison."""
    print("\n  Transport : Car")
    print(f"  Duration  : {car_duration} minutes")

    if car_cost is not None:
        print(f"  Cost      : {car_cost:.2f} SAR (estimated fuel)")
    else:
        print("  Cost      : Distance unavailable")

    print(f"  Traffic   : {period}")


def _print_metro_unavailable() -> None:
    """Print the metro part when no route could be found."""
    print("  Duration  : Route unavailable")
    print("  Cost      : Not estimated")
    print(
        "  Note      : No metro route found. Either a station name "
        "was not recognized, or the stations are on different lines."
    )
    print("\n  Recommendation unavailable for metro comparison.")


def compare_transport_options(
    origin: str,
    destination: str,
    departure_time: str,
    interactive: bool = True,
) -> dict | None:
    """Compare car and metro for a trip and print the result.

    Args:
        origin: Starting location.
        destination: Destination.
        departure_time: Time in ``HH:MM`` format.
        interactive: If True, ask for a priority, print a recommendation
            and show a chart when a metro route exists.

    Returns:
        A dict with the comparison data to save, or None if the route is
        not in the sample data.
    """
    route = find_transport_options(origin, destination)

    if route is None:
        print("\nTransport comparison is not available for this route yet.")
        return None

    distance_km = route.get("distance_km")
    base_minutes = route["base_duration_minutes"]

    period, car_duration = estimate_trip_duration(
        base_minutes, departure_time
    )
    car_cost = calculate_car_fuel_cost(distance_km)

    metro_route = find_metro_route(origin, destination)
    metro_duration = None

    if metro_route is not None:
        metro_duration = estimate_metro_route_duration(metro_route)

    print("\n" + "=" * 42)
    print("          TRANSPORT COMPARISON")
    print("=" * 42)
    print(f"  From      : {origin}")
    print(f"  To        : {destination}")
    print(f"  Departure : {departure_time}")
    print(f"  Distance  : {distance_km} km")
    print("-" * 42)

    _print_car_section(car_duration, car_cost, period)

    print("\n  Transport : Metro")

    if metro_route is not None and metro_duration is not None:
        print(f"  Line      : {metro_route['metro_line']}")
        print(f"  Stations  : {metro_route['number_of_stations']}")
        print(f"  Duration  : About {metro_duration} minutes")
        print(f"  Cost      : About {METRO_COST_SAR:.2f} SAR")
        print("  Note      : Estimated time, including average waiting time.")

        if interactive:
            print()
            priority = choose_trip_priority()
            display_smart_trip_summary(
                origin, destination, car_duration, car_cost,
                metro_duration, METRO_COST_SAR, priority,
            )
            show_transport_chart(
                car_duration, metro_duration, origin, destination
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
        "metro_cost": METRO_COST_SAR if metro_duration is not None else None,
        "metro_line": metro_route["metro_line"] if metro_route else None,
        "traffic_period": period,
    }
