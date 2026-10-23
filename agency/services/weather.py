import json
import urllib.error
import urllib.parse
import urllib.request

from agency.errors import ServiceError
from agency.models.country import Country

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 6


COUNTRY_ALIASES = {
    "uae": "united arab emirates",
    "usa": "united states",
    "turkey": "türkiye",
}


WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail",
}


def describe(code) -> str:
    return WEATHER_CODES.get(code, "Unknown")


def _get_json(url: str, params: dict) -> dict:
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(full_url, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    except (OSError, ValueError):
        raise ServiceError("Live weather is unavailable right now. "
                           "Check your internet connection and try again.")


def _find_location(destination: Country) -> dict:
    data = _get_json(GEOCODING_URL, {"name": destination.city, "count": 10, "language": "en"})
    results = data.get("results") or []
    if not results:
        raise ServiceError(f"The weather service could not find {destination.city}.")

    wanted = destination.country.lower()
    accepted = {wanted, COUNTRY_ALIASES.get(wanted, wanted)}
    for result in results:
        name = result.get("country", "").lower()
        if name and any(option in name or name in option for option in accepted):
            return result
    return results[0]


def get_forecast(destination: Country) -> dict:
    location = _find_location(destination)
    data = _get_json(FORECAST_URL, {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 4,
        "timezone": "auto",
    })
    try:
        current = data["current"]
        daily = data["daily"]
        days = [
            {"date": date, "max": high, "min": low, "condition": describe(code)}
            for date, high, low, code in zip(daily["time"], daily["temperature_2m_max"],
                                             daily["temperature_2m_min"], daily["weather_code"])
        ]
        return {
            "city": destination.city,
            "temperature": current["temperature_2m"],
            "wind": current["wind_speed_10m"],
            "condition": describe(current["weather_code"]),
            "days": days,
        }
    except (KeyError, TypeError):
        raise ServiceError("The weather service returned unexpected data.")
