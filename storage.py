
import json
import os


def load_trips():
    if not os.path.exists("trips.json"):
        return []

    try:
        with open("trips.json", "r", encoding="utf-8") as file:
            trips = json.load(file)

        if not isinstance(trips, list):
            print("Error: Trips data must be a list.")
            return []

        return trips

    except json.JSONDecodeError:
        print("Error: trips.json contains invalid JSON.")
        return []


def save_trip(trip):
    trips = load_trips()

    trips.append(trip)

    with open("trips.json", "w", encoding="utf-8") as file:
        json.dump(trips, file, indent=4, ensure_ascii=False)


def update_trip(trip_index, updated_trip):
    trips = load_trips()

    if trip_index < 0 or trip_index >= len(trips):
        print("INVALID trip number.")
        return False

    trips[trip_index].update(updated_trip)

    with open("trips.json", "w", encoding="utf-8") as file:
        json.dump(trips, file, indent=4, ensure_ascii=False)

    print("Trip updated successful.")
    return True


def delete_trip(trip_index):
    trips = load_trips()

    if trip_index < 0 or trip_index >= len(trips):
        print("INVALID trip number.")
        return False

    deleted_trip = trips.pop(trip_index)

    with open("trips.json", "w", encoding="utf-8") as file:
        json.dump(trips, file, indent=4, ensure_ascii=False)

    print("Trip deleted successful!")
    return deleted_trip
