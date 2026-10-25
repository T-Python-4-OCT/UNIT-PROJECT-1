from models import Trip
from datetime import datetime
from traffic_data import estimate_trip_duration
import json
from storage import save_trip
from transport_advisor import compare_transport_options

def load_routes():
    with open("routes.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["routes"]


def plan_trip():
    print("\n----PLAN a Trip----")

    origin = input("Enter starting location:").strip()
    destination = input("Enter destination:").strip()

    if not origin or not destination:
        print("Error: loactions cannot be empty!")
        return None

    departure_time = input("Enter departure time (HH:MM):").strip()

    try:
        datetime.strptime(departure_time, "%H:%M")
    except ValueError:
        print("Invalid time. Please use HH:MM, for example 08:30.")
        return None

    routes = load_routes()
    route = None

    for item in routes:
        if (
            item["origin"].lower() == origin.lower()
            and item["destination"].lower() == destination.lower()
        ):
            route = item
            break

    if route is None:
        print("Sorry,this route is not available in our sample data")
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
        estimated_minutes
)
    
    
    save_trip({
        "origin": trip.origin,
        "destination": trip.destination,
        "departure_time": trip.departure_time,
        "base_minutes": trip.base_minutes,
        "traffic_period": trip.traffic_period,
        "estimated_minutes": trip.estimated_minutes
})
    

    print("\n" + "=" * 40)
    print("           TRIP SUMMARY")
    print("=" * 40)
    trip.display_trip()
    print("=" * 40)
    print("  Trip saved successfully!")
    
    compare_transport_options(
        trip.origin,
        trip.destination,
        trip.departure_time
    )

    return trip
