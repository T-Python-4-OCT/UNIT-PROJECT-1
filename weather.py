import requests


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather(city):
    latitude = city["latitude"]
    longitude = city["longitude"]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        return {
            "temperature": current.get("temperature_2m"),
            "weather_code": current.get("weather_code"),
        }

    except requests.RequestException:
        return None


def get_weather_description(weather_code):
    return WEATHER_CODES.get(
        weather_code,
        "Unknown weather",
    )


def show_weather(city):
    print("\n" + "=" * 50)
    print(f"🌤️ Weather in {city['name']}")
    print("=" * 50)

    print("Loading live weather data...")

    weather = get_weather(city)

    if not weather:
        print("❌ Could not retrieve weather data.")
        return

    temperature = weather["temperature"]
    weather_code = weather["weather_code"]

    description = get_weather_description(weather_code)

    print(f"\n📍 City: {city['name']}")
    print(f"🌡️ Temperature: {temperature}°C")
    print(f"☁️ Condition: {description}")