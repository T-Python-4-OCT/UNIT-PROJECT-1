
import json
from traffic_data import estimate_trip_duration


FUEL_PRICE_SAR = 2.18
FUEL_CONSUMPTION_PER_100_KM = 6


def load_routes():
    with open("routes.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["routes"]


def find_transport_options(origin, destination):
    routes = load_routes()

    for route in routes:
        if (
            route["origin"].lower() == origin.lower()
            and route["destination"].lower() == destination.lower()
        ):
            return route

    return None


def calculate_car_fuel_cost(distance_km):
    if distance_km is None or distance_km <= 0:
        return None

    fuel_liters = distance_km * FUEL_CONSUMPTION_PER_100_KM / 100
    return round(fuel_liters * FUEL_PRICE_SAR, 2)


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

    # Sample metro information
    metro_duration = 40
    metro_cost = 4

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
    print(f"  Duration  : {metro_duration} minutes")
    print(f"  Cost      : {metro_cost:.2f} SAR")

    print("\n" + "-" * 42)
    print("          RECOMMENDATIONS")
    print("-" * 42)

    if car_duration < metro_duration:
        print("  Fastest option : Car")
    elif metro_duration < car_duration:
        print("  Fastest option : Metro")
    else:
        print("  Fastest option : Both options have equal duration")

    if car_cost is not None and car_cost < metro_cost:
        print("  Cheapest option: Car (fuel estimate only)")
    else:
        print("  Cheapest option: Metro (based on listed fares)")

    print("=" * 42)

    return {
        "distance_km": distance_km,
        "car_duration": car_duration,
        "car_cost": car_cost,
        "metro_duration": metro_duration,
        "metro_cost": metro_cost,
        "traffic_period": period
    }
