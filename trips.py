
from datetime import datetime
from traffic_data import estimate_trip_duration
import json
from storage import save_trip


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

    trip = {
        "origin": origin,
        "destination": destination,
        "departure_time": departure_time,
        "base_minutes": base_minutes,
        "traffic_period": period,
        "estimated_minutes": estimated_minutes
    }
    
    save_trip(trip)
    

    print("\n ----Trip Estimate----")
    print(f"from:{origin}")
    print(f"To: {destination}")
    print(f"Departure: {departure_time}")
    print(f"Traffic period: {period}")
    print(f"Estimated duration: {estimated_minutes} Minutes")

    return trip
