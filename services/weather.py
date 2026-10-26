from datetime import datetime

import requests

from utils.file_handler import WEATHER_CACHE_FILE, load_json, save_json

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10
FORECAST_DAYS = 7
DAILY_VARIABLES = (
    "temperature_2m_max,temperature_2m_min,precipitation_sum,"
    "wind_speed_10m_max,et0_fao_evapotranspiration"
)


class WeatherError(Exception):
    """Raised when weather data cannot be obtained from the API or the cache."""


def find_city(city):
    """Look up a city name and return its coordinates and a readable name."""
    response = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        raise WeatherError(f"City '{city}' was not found. Check the spelling and try again.")
    place = results[0]
    name_parts = [place.get("name"), place.get("country")]
    return {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "location_name": ", ".join(part for part in name_parts if part),
    }


def number_or_zero(value):
    """The API can return null for a day; treat it as 0."""
    return 0 if value is None else value


def build_daily_list(daily):
    """Turn the API's column-style data into a list of one dictionary per day."""
    days = []
    for date, temp_max, temp_min, rain, wind, et0 in zip(
        daily["time"],
        daily["temperature_2m_max"],
        daily["temperature_2m_min"],
        daily["precipitation_sum"],
        daily["wind_speed_10m_max"],
        daily["et0_fao_evapotranspiration"],
    ):
        days.append({
            "date": date,
            "temp_max": number_or_zero(temp_max),
            "temp_min": number_or_zero(temp_min),
            "rain_mm": number_or_zero(rain),
            "wind_max": number_or_zero(wind),
            "et0_mm": number_or_zero(et0),
        })
    return days


def fetch_forecast(latitude, longitude):
    """Download the current weather and the daily forecast for a location."""
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m",
            "daily": DAILY_VARIABLES,
            "forecast_days": FORECAST_DAYS,
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "current": {
            "temperature": data["current"]["temperature_2m"],
            "wind_speed": data["current"]["wind_speed_10m"],
        },
        "daily": build_daily_list(data["daily"]),
    }


def get_weather(city):
    """Return (weather, from_cache) for a city.

    Tries the API first. If the internet is unavailable, falls back to the
    last saved data for this city. Raises WeatherError if neither works.
    """
    cache = load_json(WEATHER_CACHE_FILE, {})
    key = city.strip().lower()
    cached = cache.get(key)

    try:
        place = cached if cached else find_city(city)
        weather = fetch_forecast(place["latitude"], place["longitude"])
    except (requests.RequestException, ValueError, KeyError):
        if cached:
            return cached, True
        raise WeatherError("No internet connection and no saved weather data for this city.")

    weather["latitude"] = place["latitude"]
    weather["longitude"] = place["longitude"]
    weather["location_name"] = place["location_name"]
    weather["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    cache[key] = weather
    save_json(WEATHER_CACHE_FILE, cache)
    return weather, False