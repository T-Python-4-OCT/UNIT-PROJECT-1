
import requests
import json

API_URL = (
    "https://opendata.rcrc.gov.sa/api/explore/v2.1/"
    "catalog/datasets/"
    "metro-stations-in-riyadh-by-metro-line-and-station-type-2024/"
    "records"
)


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
            "metro_line": station.get(
                "metro_line_desc_en", "Unknown"
            ),
            "latitude": coordinates.get("lat"),
            "longitude": coordinates.get("lon"),
            "data_source": "RCRC Open Data"
        }

        if (
            location["latitude"] is not None
            and location["longitude"] is not None
        ):
            locations.append(location)

        if len(locations) == 30:
            break

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


if __name__ == "__main__":
    try:
        stations = load_metro_stations()

        print(f"\nMetro stations loaded: {len(stations)}")

        save_locations(stations)

    except (requests.RequestException, ValueError, KeyError) as error:
        print("Could not load metro station data.")
        print(error)
