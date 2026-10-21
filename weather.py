import requests


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,weather_code",
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def show_weather(city):
    weather_data = get_weather(
        city["latitude"],
        city["longitude"]
    )

    current = weather_data["current"]

    print()
    print("🌤️ Current Weather")
    print(f"📍 City: {city['name']}")
    print(f"🌡️ Temperature: {current['temperature_2m']} °C")
    print(f"💧 Humidity: {current['relative_humidity_2m']}%")
    print(f"🌐 Weather Code: {current['weather_code']}")