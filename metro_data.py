
import requests
import json

API_URL = (
    "https://opendata.rcrc.gov.sa/api/explore/v2.1/"
    "catalog/datasets/"
    "metro-stations-in-riyadh-by-metro-line-and-station-type-2024/"
    "records"
)

# Approximate full-line journey times in minutes.
# These are estimates, not live timetable data.

METRO_LINE_TIMES = {
    "Line1": {"stations": 25, "min_minutes": 35, "max_minutes": 45},
    "Line2": {"stations": 15, "min_minutes": 25, "max_minutes": 30},
    "Line3": {"stations": 22, "min_minutes": 40, "max_minutes": 50},
    "Line4": {"stations": 9, "min_minutes": 20, "max_minutes": 25},
    "Line5": {"stations": 12, "min_minutes": 15, "max_minutes": 20},
    "Line6": {"stations": 11, "min_minutes": 25, "max_minutes": 30},
}


def load_metro_stations():
    response = requests.get(
        API_URL,
        params={"limit": 100},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()
    return data["results"]


def save_locations(stations):
    locations = []

    for station in stations:
        coordinates = station.get("geo_point_2d")

        if not coordinates:
            continue

        location = {
            "name": station.get(
                "metro_station_desc_en", "Unknown"
            ),
            "name_ar": station.get(
                "metro_station_desc_ar", "غير معروف"
            ),
            "type": "Metro Station",
            "station_code": station.get(
                "metro_station_cd"
            ),
            "metro_line": station.get(
                "metro_line_desc_en", "Unknown"
            ),
            "metro_line_code": station.get(
                "metro_line_cd"
            ),
            "station_sequence": station.get(
                "metro_station_seq"
            ),
            "latitude": coordinates.get("lat"),
            "longitude": coordinates.get("lon"),
            "data_source": "RCRC Open Data"
        }

        if (
            location["latitude"] is not None
            and location["longitude"] is not None
            and location["station_sequence"] is not None
        ):
            locations.append(location)

    with open(
        "locations.json", "w", encoding="utf-8"
    ) as file:
        json.dump(
            locations,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"Locations saved: {len(locations)}")
    print("File: locations.json")



def find_metro_route(origin, destination):
    with open(
        "locations.json", "r", encoding="utf-8"
    ) as file:
        locations = json.load(file)

    origin = origin.strip().lower()
    destination = destination.strip().lower()

    origin_matches = [
        station for station in locations
        if origin in station["name"].lower()
        or origin in station["name_ar"].lower()
    ]

    destination_matches = [
        station for station in locations
        if destination in station["name"].lower()
        or destination in station["name_ar"].lower()
    ]

    if not origin_matches or not destination_matches:
        return None

    possible_routes = []

    for origin_station in origin_matches:
        for destination_station in destination_matches:
            if (
                origin_station["metro_line_code"]
                == destination_station["metro_line_code"]
            ):
                station_difference = abs(
                    origin_station["station_sequence"]
                    - destination_station["station_sequence"]
                )

                possible_routes.append({
                    "origin": origin_station["name"],
                    "destination": destination_station["name"],
                    "metro_line": origin_station["metro_line"],
                    "metro_line_code": origin_station[
                        "metro_line_code"
                    ],
                    "number_of_stations": station_difference,
                    "number_of_stops": station_difference
                })

    if not possible_routes:
        return None

    return min(
        possible_routes,
        key=lambda route: route["number_of_stations"]
    )


def estimate_metro_route_duration(route, waiting_minutes=6.5):
    line_code = route["metro_line_code"]
    station_count = route["number_of_stations"]

    line_data = METRO_LINE_TIMES.get(line_code)

    if line_data is None:
        return None

    if station_count < 0 or waiting_minutes < 0:
        return None

    # Estimate travel time using the full-line average.
    intervals = line_data["stations"] - 1

    if intervals <= 0:
        return None

    average_line_minutes = (
        line_data["min_minutes"] + line_data["max_minutes"]
    ) / 2

    travel_minutes = (
        station_count / intervals
    ) * average_line_minutes

    return round(travel_minutes + waiting_minutes)


if __name__ == "__main__":
    try:
        stations = load_metro_stations()

        print(f"\nMetro stations loaded: {len(stations)}")

        save_locations(stations)

    except (requests.RequestException, ValueError, KeyError) as error:
        print("Could not load metro station data.")
        print(error)
