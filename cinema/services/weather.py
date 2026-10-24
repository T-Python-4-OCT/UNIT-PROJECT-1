"""Real weather forecast for the show day, using the free Open-Meteo API (no key needed)."""

import requests

from cinema.config.settings import CITY_LATITUDE, CITY_LONGITUDE, CITY_NAME

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(show_date: str) -> dict | None:
    """Return {'max': .., 'min': .., 'rain': ..} or None if there is no internet."""
    params = {
        "latitude": CITY_LATITUDE,
        "longitude": CITY_LONGITUDE,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Riyadh",
        "start_date": show_date,
        "end_date": show_date,
    }
    try:
        response = requests.get(WEATHER_URL, params=params, timeout=5)
        response.raise_for_status()
        daily = response.json()["daily"]
        return {
            "max": daily["temperature_2m_max"][0],
            "min": daily["temperature_2m_min"][0],
            "rain": daily["precipitation_probability_max"][0] or 0,
        }
    except (requests.RequestException, KeyError, IndexError, ValueError, TypeError):
        return None


def weather_tip(weather: dict) -> str:
    if weather["rain"] >= 50:
        return "Rain is expected - leave early, traffic may be heavy!"
    if weather["max"] >= 40:
        return "Very hot day - enjoy the cold cinema AC!"
    if weather["min"] <= 15:
        return "Cool evening - take a jacket with you."
    return "Nice weather - enjoy your movie!"


def print_weather(show_date: str) -> None:
    weather = get_weather(show_date)
    if weather is None:
        print("Weather: not available right now (check your internet connection).")
        return
    print(f"Weather in {CITY_NAME} on {show_date}: "
          f"{weather['min']:.0f}°C - {weather['max']:.0f}°C, rain chance {weather['rain']}%")
    print(f"Tip: {weather_tip(weather)}")
