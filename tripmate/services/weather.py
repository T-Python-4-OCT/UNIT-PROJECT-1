from datetime import date

import requests

from rich.markup import escape
from rich.panel import Panel

from tripmate.core.colors import (
    console,
    error,
    warning
)

from tripmate.core.config import (
    FORECAST_DAYS_LIMIT,
    REQUEST_TIMEOUT
)

from tripmate.core.utils import (
    parse_date
)


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Rain showers",
    82: "Heavy rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail",
}


def get_weather_description(
    weather_code
) -> str:

    return WEATHER_CODES.get(
        weather_code,
        "Unknown weather"
    )


def _get_json(
    url: str,
    params: dict,
    error_message: str
):

    try:

        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT
        )


        response.raise_for_status()


        return response.json()


    except (
        requests.RequestException,
        ValueError
    ):

        error(
            error_message
        )

        return None


def _first(
    values: dict,
    key: str
):

    series = (
        values.get(
            key
        )
        or
        []
    )


    if series:

        return series[0]


    return None


def _show(
    value,
    unit: str = ""
) -> str:

    if value is None:

        return "N/A"


    return f"{value}{unit}"


def _at_most(
    value,
    limit
) -> bool:

    return (
        value is not None
        and
        value <= limit
    )


def _at_least(
    value,
    limit
) -> bool:

    return (
        value is not None
        and
        value >= limit
    )


def find_location(
    city: str,
    country: str,
    silent: bool = False
):

    data = _get_json(
        GEOCODING_URL,
        {
            "name": city,
            "count": 10,
            "language": "en",
            "format": "json"
        },
        (
            "Could not connect to "
            "the location service."
        )
    )


    if data is None:

        return None


    results = data.get(
        "results"
    )


    if not results:

        if not silent:

            error(
                "Location not found."
            )

        return None


    for result in results:

        if (
            str(
                result.get(
                    "country",
                    ""
                )
            ).lower()
            ==
            country.lower()
        ):

            return result


    if not silent:

        closest = results[0]

        warning(
            f"Could not verify {city} "
            f"inside {country}. "
            f"The closest result was "
            f"{closest.get('name')}, "
            f"{closest.get('country')}."
        )


    return None

    data = _get_json(
        GEOCODING_URL,
        {
            "name": city,
            "count": 10,
            "language": "en",
            "format": "json"
        },
        (
            "Could not connect to "
            "the location service."
        )
    )


    if data is None:

        return None


    results = data.get(
        "results"
    )


    if not results:

        error(
            "Location not found."
        )

        return None


    for result in results:

        if (
            str(
                result.get(
                    "country",
                    ""
                )
            ).lower()
            ==
            country.lower()
        ):

            return result


    closest = results[0]


    warning(
        f"Could not verify {city} "
        f"inside {country}. "
        f"The closest result was "
        f"{closest.get('name')}, "
        f"{closest.get('country')}, "
        f"so it was not accepted "
        f"automatically."
    )


    return None


def get_current_weather(
    latitude: float,
    longitude: float
):

    data = _get_json(
        WEATHER_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "apparent_temperature,"
                "relative_humidity_2m,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto"
        },
        (
            "Could not connect to "
            "the weather service."
        )
    )


    if data is None:

        return None


    current = data.get(
        "current"
    )


    if current is None:

        error(
            "Current weather data "
            "is unavailable."
        )

        return None


    return {
        "temperature": current.get(
            "temperature_2m"
        ),
        "feels_like": current.get(
            "apparent_temperature"
        ),
        "humidity": current.get(
            "relative_humidity_2m"
        ),
        "wind_speed": current.get(
            "wind_speed_10m"
        ),
        "condition": (
            get_weather_description(
                current.get(
                    "weather_code"
                )
            )
        )
    }


def get_trip_forecast(
    latitude: float,
    longitude: float,
    trip_date: str
):

    data = _get_json(
        WEATHER_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "apparent_temperature_max,"
                "apparent_temperature_min,"
                "precipitation_probability_max,"
                "wind_speed_10m_max"
            ),
            "timezone": "auto",
            "start_date": trip_date,
            "end_date": trip_date
        },
        (
            "Could not retrieve "
            "the trip forecast."
        )
    )


    if data is None:

        return None


    daily = data.get(
        "daily"
    )


    if (
        not daily
        or
        not daily.get(
            "time"
        )
    ):

        return None


    return {
        "date": daily["time"][0],
        "condition": (
            get_weather_description(
                _first(
                    daily,
                    "weather_code"
                )
            )
        ),
        "max_temperature": _first(
            daily,
            "temperature_2m_max"
        ),
        "min_temperature": _first(
            daily,
            "temperature_2m_min"
        ),
        "max_feels_like": _first(
            daily,
            "apparent_temperature_max"
        ),
        "min_feels_like": _first(
            daily,
            "apparent_temperature_min"
        ),
        "rain_probability": _first(
            daily,
            "precipitation_probability_max"
        ),
        "max_wind_speed": _first(
            daily,
            "wind_speed_10m_max"
        )
    }


def get_current_recommendation(
    weather: dict
) -> str:

    recommendations = []


    temperature = weather[
        "temperature"
    ]

    condition = weather[
        "condition"
    ].lower()


    if temperature is not None:

        if temperature <= 10:

            recommendations.append(
                "Take warm clothing."
            )


        elif temperature >= 30:

            recommendations.append(
                "Wear light clothes "
                "and stay hydrated."
            )


        else:

            recommendations.append(
                "The temperature is suitable "
                "for outdoor activities."
            )


    if (
        "rain" in condition
        or
        "drizzle" in condition
    ):

        recommendations.append(
            "Take an umbrella."
        )


    if "snow" in condition:

        recommendations.append(
            "Wear warm and waterproof "
            "clothes."
        )


    if "thunderstorm" in condition:

        recommendations.append(
            "Avoid outdoor activities "
            "during the storm."
        )


    if not recommendations:

        return (
            "Check the weather again "
            "before going out."
        )


    return " ".join(
        recommendations
    )


def get_forecast_recommendation(
    forecast: dict
) -> str:

    recommendations = []


    condition = forecast[
        "condition"
    ].lower()


    if _at_most(
        forecast[
            "min_temperature"
        ],
        10
    ):

        recommendations.append(
            "Pack warm clothing."
        )


    if _at_least(
        forecast[
            "max_temperature"
        ],
        30
    ):

        recommendations.append(
            "Pack light clothes "
            "and stay hydrated."
        )


    if _at_least(
        forecast[
            "rain_probability"
        ],
        50
    ):

        recommendations.append(
            "There is a good chance "
            "of rain, so take an umbrella."
        )


    if "snow" in condition:

        recommendations.append(
            "Prepare for snowy weather "
            "and pack waterproof clothing."
        )


    if "thunderstorm" in condition:

        recommendations.append(
            "Outdoor plans may need "
            "to be adjusted."
        )


    if not recommendations:

        recommendations.append(
            "Weather conditions look "
            "generally comfortable."
        )


    return " ".join(
        recommendations
    )


def _location_name(
    location: dict
) -> str:

    return escape(
        f"{location.get('name')}, "
        f"{location.get('country')}"
    )


def display_current_weather(
    location: dict
):

    weather = get_current_weather(
        location["latitude"],
        location["longitude"]
    )


    if weather is None:

        return


    text = (
        f"[bold]Location:[/bold] "
        f"{_location_name(location)}\n\n"

        f"[bold]Temperature:[/bold] "
        f"{_show(weather['temperature'], ' °C')}\n"

        f"[bold]Feels Like:[/bold] "
        f"{_show(weather['feels_like'], ' °C')}\n"

        f"[bold]Condition:[/bold] "
        f"{weather['condition']}\n"

        f"[bold]Humidity:[/bold] "
        f"{_show(weather['humidity'], '%')}\n"

        f"[bold]Wind Speed:[/bold] "
        f"{_show(weather['wind_speed'], ' km/h')}\n\n"

        f"[bold cyan]Recommendation:"
        f"[/bold cyan]\n"

        f"{get_current_recommendation(weather)}"
    )


    console.print()


    console.print(
        Panel(
            text,
            title="Current Weather",
            border_style="blue"
        )
    )


def display_trip_forecast(
    location: dict,
    start_date: str
):

    forecast = get_trip_forecast(
        location["latitude"],
        location["longitude"],
        start_date
    )


    if forecast is None:

        error(
            "Forecast is currently "
            "unavailable."
        )

        return


    text = (
        f"[bold]Location:[/bold] "
        f"{_location_name(location)}\n"

        f"[bold]Trip Date:[/bold] "
        f"{forecast['date']}\n\n"

        f"[bold]Condition:[/bold] "
        f"{forecast['condition']}\n"

        f"[bold]Maximum Temperature:[/bold] "
        f"{_show(forecast['max_temperature'], ' °C')}\n"

        f"[bold]Minimum Temperature:[/bold] "
        f"{_show(forecast['min_temperature'], ' °C')}\n"

        f"[bold]Feels Like:[/bold] "
        f"{_show(forecast['min_feels_like'], ' °C')}"
        f" - "
        f"{_show(forecast['max_feels_like'], ' °C')}\n"

        f"[bold]Rain Probability:[/bold] "
        f"{_show(forecast['rain_probability'], '%')}\n"

        f"[bold]Maximum Wind Speed:[/bold] "
        f"{_show(forecast['max_wind_speed'], ' km/h')}\n\n"

        f"[bold cyan]Travel Recommendation:"
        f"[/bold cyan]\n"

        f"{get_forecast_recommendation(forecast)}"
    )


    console.print()


    console.print(
        Panel(
            text,
            title="Trip Weather Forecast",
            border_style="green"
        )
    )


def display_weather_for_trip(
    trip
):

    location = find_location(
        trip.city,
        trip.country
    )


    if location is None:

        return


    try:

        days_until_trip = (
            parse_date(
                trip.start_date
            )
            -
            date.today()
        ).days


    except ValueError:

        error(
            "This trip has an invalid "
            "start date."
        )

        return


    if days_until_trip == 0:

        console.print(
            "\n[cyan]"
            "Your trip starts today."
            "[/cyan]"
        )

        display_current_weather(
            location
        )


    elif (
        1
        <=
        days_until_trip
        <=
        FORECAST_DAYS_LIMIT
    ):

        console.print(
            f"\n[cyan]"
            f"Your trip starts in "
            f"{days_until_trip} day(s)."
            f"[/cyan]"
        )

        display_trip_forecast(
            location,
            trip.start_date
        )


    elif days_until_trip < 0:

        warning(
            "This trip date is in the past."
        )

        display_current_weather(
            location
        )


    else:

        console.print(
            "\n[yellow]"
            "An accurate forecast is not "
            "available yet because your trip "
            f"is {days_until_trip} days away."
            "[/yellow]"
        )

        console.print(
            "[yellow]"
            "Trip forecasts are available "
            "when the departure date is within "
            f"{FORECAST_DAYS_LIMIT} days."
            "[/yellow]"
        )

        console.print(
            "\nCurrent weather is shown "
            "below for reference only."
        )

        display_current_weather(
            location
        )