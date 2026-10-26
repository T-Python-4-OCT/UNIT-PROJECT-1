import questionary
import json
from traffic_data import estimate_trip_duration
from trip_charts import show_transport_chart
from metro_data import find_metro_route, estimate_metro_route_duration

FUEL_PRICE_SAR = 2.18
FUEL_CONSUMPTION_PER_100_KM = 6


def choose_trip_priority():
    choice = questionary.select(
        "Choose your trip priority:",
        choices=[
            "Fastest Trip",
            "Lowest Cost",
            "Best Balance (Time + Cost)"
        ]
    ).ask()

    if choice == "Fastest Trip":
        return "fastest"
    elif choice == "Lowest Cost":
        return "cheapest"
    elif choice == "Best Balance (Time + Cost)":
        return "balanced"
    else:
        return None


def load_routes():
    with open("routes.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["routes"]



def find_transport_options(origin, destination):
    routes = load_routes()

    def normalize_location(location):
        return (
            location.strip()
            .lower()
            .replace("oo", "u")
            .replace(" ", "")
        )

    origin = normalize_location(origin)
    destination = normalize_location(destination)

    for route in routes:
        route_origin = normalize_location(route["origin"])
        route_destination = normalize_location(route["destination"])

        if (
            route_origin == origin
            and route_destination == destination
        ):
            return route

    return None


def calculate_car_fuel_cost(distance_km):
    if distance_km is None or distance_km <= 0:
        return None

    fuel_liters = distance_km * FUEL_CONSUMPTION_PER_100_KM / 100
    return round(fuel_liters * FUEL_PRICE_SAR, 2)


def display_smart_trip_summary(
    origin, destination, car_duration, car_cost,
    metro_duration, metro_cost, priority
):
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

    if priority == "fastest":
        recommended = (
            "Car" if car_duration <= metro_duration else "Metro"
        )
        reason = "It has the shorter estimated travel time."

    elif priority == "cheapest":
        if car_cost is None:
            recommended = None
            reason = "The car cost cannot be calculated."
        else:
            recommended = "Car" if car_cost <= metro_cost else "Metro"
            reason = "It has the lower estimated cost."

    else:
        if car_cost is None:
            recommended = None
            reason = (
                "The car cost is unavailable, so a balanced "
                "comparison cannot be made."
            )
        else:
            car_score = (
                car_duration / max(car_duration, metro_duration)
                + car_cost / max(car_cost, metro_cost)
            )
            metro_score = (
                metro_duration / max(car_duration, metro_duration)
                + metro_cost / max(car_cost, metro_cost)
            )

            recommended = "Car" if car_score <= metro_score else "Metro"
            reason = "It has the lower combined time-and-cost score."

    print("\n  YOUR RECOMMENDATION")

    if recommended is None:
        print("  No recommendation available.")
    else:
        print(f"  Recommended option: {recommended}")
        print(f"  Reason: {reason}")

    print("=" * 42)
    return recommended


def compare_transport_options(origin, destination, departure_time):
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

    # Find the metro route between the selected stations
    metro_route = find_metro_route(origin, destination)
    print("DEBUG origin:", repr(origin))
    print("DEBUG metro_route:", metro_route)

    metro_duration = None
    metro_cost = 4

    if metro_route is not None:
        metro_duration = estimate_metro_route_duration(metro_route)

    priority = choose_trip_priority()

    print("\n" + "=" * 42)
    print("          TRANSPORT COMPARISON")
    print("=" * 42)
    print(f"  From      : {origin}")
    print(f"  To        : {destination}")
    print(f"  Departure : {departure_time}")
    print(f"  Distance  : {distance_km} km")
    print("-" * 42)

    print("\n  Transport : Car")
    print(f"  Duration  : {car_duration} minutes")
    print(
        f"  Cost      : {car_cost:.2f} SAR (estimated fuel)"
        if car_cost is not None
        else "  Cost      : Distance unavailable"
    )
    print(f"  Traffic   : {period}")

    print("\n  Transport : Metro")

    if metro_route is not None and metro_duration is not None:
        print(f"  Line      : {metro_route['metro_line']}")
        print(f"  Stations  : {metro_route['number_of_stations']}")
        print(f"  Duration  : About {metro_duration} minutes")
        print(f"  Cost      : About {metro_cost:.2f} SAR")
        print("  Note      : Estimated time, including average waiting time.")

        display_smart_trip_summary(
            origin,
            destination,
            car_duration,
            car_cost,
            metro_duration,
            metro_cost,
            priority
        )

        show_transport_chart(
            car_duration,
            metro_duration,
            origin,
            destination
        )

    else:
        print("  Duration  : Route unavailable")
        print("  Cost      : Not estimated")
        print(
            "  Note      : No matching metro line was found "
            "between these stations."
        )
        print("\n  Recommendation unavailable for metro comparison.")

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
        "metro_cost": metro_cost if metro_duration is not None else None,
        "metro_line": metro_route["metro_line"] if metro_route else None,
        "traffic_period": period
    }
