
import requests


def show_weather():
    city = input("Enter city name: ").strip()

    if not city:
        print("Please enter a city name.")
        return

    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url, params=geo_params, timeout=10
        )
        geo_response.raise_for_status()

        geo_data = geo_response.json()
        results = geo_data.get("results", [])

        if not results:
            print("City not found. Please try again.")
            return

        location = results[0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "Unknown")

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,wind_speed_10m,weather_code"
            ),
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url, params=weather_params, timeout=10
        )
        weather_response.raise_for_status()

        data = weather_response.json()
        current = data["current"]

        print("\n" + "=" * 40)
        print(f"WEATHER IN {city_name.upper()}, {country.upper()}")
        print("=" * 40)

        print(f"Temperature: {current['temperature_2m']} °C")
        print(f"Feels like: {current['apparent_temperature']} °C")
        print(f"Humidity: {current['relative_humidity_2m']}%")
        print(f"Wind speed: {current['wind_speed_10m']} km/h")
        print(f"Weather code: {current['weather_code']}")
        print(f"Updated at: {current['time']}")

        print("=" * 40)

    except requests.exceptions.RequestException as error:
        print(f"Weather API error: {error}")
    except (KeyError, IndexError, ValueError):
        print("Could not read the weather data. Please try again.")
