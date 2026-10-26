"""Save, load, update and delete trips stored in a JSON file."""
from __future__ import annotations

import json
import os

TRIPS_FILE = "trips.json"


def load_trips() -> list[dict]:
    """Load saved trips. Return an empty list if none can be loaded."""
    if not os.path.exists(TRIPS_FILE):
        return []

    try:
        with open(TRIPS_FILE, "r", encoding="utf-8") as file:
            trips = json.load(file)
    except json.JSONDecodeError:
        print(f"Error: {TRIPS_FILE} contains invalid JSON.")
        return []

    if not isinstance(trips, list):
        print("Error: Trips data must be a list.")
        return []

    return trips


def _write_trips(trips: list[dict]) -> None:
    """Write the full list of trips to the JSON file."""
    with open(TRIPS_FILE, "w", encoding="utf-8") as file:
        json.dump(trips, file, indent=4, ensure_ascii=False)


def save_trip(trip: dict) -> None:
    """Append a trip to the saved trips."""
    trips = load_trips()
    trips.append(trip)
    _write_trips(trips)


def update_trip(trip_index: int, updated_trip: dict) -> bool:
    """Merge new values into a saved trip. Return True on success."""
    trips = load_trips()

    if not 0 <= trip_index < len(trips):
        print("Invalid trip number.")
        return False

    trips[trip_index].update(updated_trip)
    _write_trips(trips)

    print("Trip updated successfully.")
    return True


def delete_trip(trip_index: int) -> dict | None:
    """Delete a saved trip and return it, or None if the index is invalid."""
    trips = load_trips()

    if not 0 <= trip_index < len(trips):
        print("Invalid trip number.")
        return None

    deleted_trip = trips.pop(trip_index)
    _write_trips(trips)

    print("Trip deleted successfully.")
    return deleted_trip
