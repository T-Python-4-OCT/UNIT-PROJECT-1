"""Plan a new trip."""
from __future__ import annotations

from datetime import datetime

from models import Trip
from storage import save_trip
from traffic_data import TIME_FORMAT, estimate_trip_duration
from transport_advisor import (
    compare_transport_options,
    find_transport_options,
)


def plan_trip() -> Trip | None:
    """Ask for trip details, show the trip and comparison, and save it.

    Returns:
        The planned trip, or None if the input was invalid or the route
        is not available.
    """
    print("\n----PLAN a Trip----")

    origin = input("Enter starting location: ").strip()
    destination = input("Enter destination: ").strip()

    if not origin or not destination:
        print("Error: locations cannot be empty!")
        return None

    departure_time = input("Enter departure time (HH:MM): ").strip()

    try:
        datetime.strptime(departure_time, TIME_FORMAT)
    except ValueError:
        print("Invalid time. Please use HH:MM, for example 08:30.")
        return None

    # Same lookup as the Compare option, so both behave the same way.
    route = find_transport_options(origin, destination)

    if route is None:
        print("Sorry, this route is not available in our sample data.")
        return None

    base_minutes = route["base_duration_minutes"]
    period, estimated_minutes = estimate_trip_duration(
        base_minutes, departure_time
    )

    trip = Trip(
        origin, destination, departure_time,
        base_minutes, period, estimated_minutes,
    )

    print("\n" + "=" * 40)
    print("           TRIP SUMMARY")
    print("=" * 40)
    trip.display_trip()
    print("=" * 40)

    trip_data = trip.to_dict()

    # Add car/metro comparison data to the saved trip when available.
    result = compare_transport_options(
        trip.origin, trip.destination, trip.departure_time
    )

    if result is not None:
        trip_data.update(result)

    save_trip(trip_data)
    print("\n  Trip saved successfully!")

    return trip
