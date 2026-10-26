"""Riyadh Metro station data and metro route estimation.

Run this file directly to download the station list from RCRC Open Data
and save it to ``locations.json``. Journey times are estimates, not live
timetable data.
"""
from __future__ import annotations

import json

import requests

API_URL = (
    "https://opendata.rcrc.gov.sa/api/explore/v2.1/"
    "catalog/datasets/"
    "metro-stations-in-riyadh-by-metro-line-and-station-type-2024/"
    "records"
)
LOCATIONS_FILE = "locations.json"
API_RECORD_LIMIT = 100
DEFAULT_WAITING_MINUTES = 6.5

# Spelling used in the sample routes -> spelling used in the station data.
STATION_ALIASES = {"muruj": "murooj"}

# Approximate full-line journey times in minutes.
METRO_LINE_TIMES = {
    "Line1": {"stations": 25, "min_minutes": 35, "max_minutes": 45},
    "Line2": {"stations": 15, "min_minutes": 25, "max_minutes": 30},
    "Line3": {"stations": 22, "min_minutes": 40, "max_minutes": 50},
    "Line4": {"stations": 9, "min_minutes": 20, "max_minutes": 25},
    "Line5": {"stations": 12, "min_minutes": 15, "max_minutes": 20},
    "Line6": {"stations": 11, "min_minutes": 25, "max_minutes": 30},
}


def load_metro_stations() -> list[dict]:
    """Download the metro station records from the open data API."""
    response = requests.get(
        API_URL, params={"limit": API_RECORD_LIMIT}, timeout=20
    )
    response.raise_for_status()

    data = response.json()
    total_count = data.get("total_count")

    if total_count is not None and total_count > len(data["results"]):
        print(
            f"Warning: API has {total_count} records, "
            f"but only {len(data['results'])} were loaded."
        )

    return data["results"]


def _build_location(station: dict) -> dict | None:
    """Convert an API record to a location. Return None if incomplete."""
    coordinates = station.get("geo_point_2d")

    if not coordinates:
        return None

    location = {
        "name": station.get("metro_station_desc_en", "Unknown"),
        "name_ar": station.get("metro_station_desc_ar", "غير معروف"),
        "type": "Metro Station",
        "station_code": station.get("metro_station_cd"),
        "metro_line": station.get("metro_line_desc_en", "Unknown"),
        "metro_line_code": station.get("metro_line_cd"),
        "station_sequence": station.get("metro_station_seq"),
        "latitude": coordinates.get("lat"),
        "longitude": coordinates.get("lon"),
        "data_source": "RCRC Open Data",
    }

    required = ("latitude", "longitude", "station_sequence")

    if any(location[key] is None for key in required):
        return None

    return location


def save_locations(stations: list[dict]) -> None:
    """Save complete station records to ``locations.json``."""
    locations = [
        location
        for location in map(_build_location, stations)
        if location is not None
    ]

    with open(LOCATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(locations, file, indent=4, ensure_ascii=False)

    print(f"Locations saved: {len(locations)}")
    print(f"File: {LOCATIONS_FILE}")


def _find_stations(query: str, locations: list[dict]) -> list[dict]:
    """Return stations whose English or Arabic name contains ``query``."""
    return [
        station for station in locations
        if query in station["name"].lower()
        or query in station["name_ar"].lower()
    ]


def _normalize_query(text: str) -> str:
    """Lowercase a station query and apply known spelling aliases."""
    text = text.strip().lower()

    for alias, station_spelling in STATION_ALIASES.items():
        text = text.replace(alias, station_spelling)

    return text


def find_metro_route(
    origin: str, destination: str, locations_file: str = LOCATIONS_FILE
) -> dict | None:
    """Find the shortest metro route between two stations on one line.

    Station names are matched by part of the name. Transfers between
    lines are not supported.

    Returns:
        A route dict, or None if no route exists.
    """
    try:
        with open(locations_file, "r", encoding="utf-8") as file:
            locations = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    origin = _normalize_query(origin)
    destination = _normalize_query(destination)

    if not origin or not destination:
        return None

    possible_routes = []

    for start in _find_stations(origin, locations):
        for end in _find_stations(destination, locations):
            if start["metro_line_code"] != end["metro_line_code"]:
                continue

            station_difference = abs(
                start["station_sequence"] - end["station_sequence"]
            )

            # Same station: not a real trip.
            if station_difference == 0:
                continue

            possible_routes.append({
                "origin": start["name"],
                "destination": end["name"],
                "metro_line": start["metro_line"],
                "metro_line_code": start["metro_line_code"],
                "number_of_stations": station_difference,
                "number_of_stops": station_difference,
            })

    if not possible_routes:
        return None

    return min(possible_routes, key=lambda route: route["number_of_stations"])


def estimate_metro_route_duration(
    route: dict, waiting_minutes: float = DEFAULT_WAITING_MINUTES
) -> int | None:
    """Estimate the metro trip duration in minutes, including waiting.

    The travel time is the share of the full-line average time that
    matches the number of stations travelled.

    Returns:
        Estimated minutes, or None if the line is unknown or the input
        is invalid.
    """
    line_data = METRO_LINE_TIMES.get(route["metro_line_code"])
    station_count = route["number_of_stations"]

    if line_data is None or station_count < 0 or waiting_minutes < 0:
        return None

    intervals = line_data["stations"] - 1

    if intervals <= 0:
        return None

    average_line_minutes = (
        line_data["min_minutes"] + line_data["max_minutes"]
    ) / 2
    travel_minutes = (station_count / intervals) * average_line_minutes

    return round(travel_minutes + waiting_minutes)


if __name__ == "__main__":
    try:
        loaded_stations = load_metro_stations()
        print(f"\nMetro stations loaded: {len(loaded_stations)}")
        save_locations(loaded_stations)
    except (requests.RequestException, ValueError, KeyError) as error:
        print("Could not load metro station data.")
        print(error)
