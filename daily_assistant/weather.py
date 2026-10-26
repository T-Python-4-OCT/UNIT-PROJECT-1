import requests
from rich.panel import Panel
from rich.table import Table

from ui import console, section, error, info

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
UNKNOWN_WEATHER = ("Unknown", "🌡️")

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌧️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Light snow", "🌨️"),
    73: ("Snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"),
    81: ("Heavy showers", "🌧️"),
    82: ("Violent showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Severe thunderstorm", "⛈️"),
}


def temp_color(temp):
    if temp >= 40:
        return "bold red"
    if temp >= 30:
        return "orange1"
    if temp >= 20:
        return "yellow"
    if temp >= 10:
        return "green"
    return "cyan"


class WeatherManager:

    def get_location(self, city):
        response = requests.get(
            GEOCODING_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[0] if results else None

    def get_weather(self, location):
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "apparent_temperature,wind_speed_10m,weather_code"
                ),
                "daily": (
                    "weather_code,temperature_2m_max,"
                    "temperature_2m_min,precipitation_probability_max"
                ),
                "forecast_days": 5,
                "timezone": "auto",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def show_current_weather(self, location, weather):
        current = weather["current"]
        city = f"{location['name']}, {location.get('country', 'Unknown')}"
        description, icon = WEATHER_CODES.get(current["weather_code"], UNKNOWN_WEATHER)
        temp = current["temperature_2m"]
        time = current["time"].replace("T", " ")

        table = Table.grid(padding=(0, 3))
        table.add_column(style="dim")
        table.add_column(style="bold")
        table.add_row("Condition", f"{icon}  {description}")
        table.add_row("Temperature", f"[{temp_color(temp)}]{temp} °C[/]")
        table.add_row("Feels like", f"{current['apparent_temperature']} °C")
        table.add_row("Humidity", f"💧 {current['relative_humidity_2m']}%")
        table.add_row("Wind speed", f"💨 {current['wind_speed_10m']} km/h")
        table.add_row("Updated", time)

        console.print(
            Panel(
                table,
                title=f"[bold]{city}[/]",
                border_style="blue",
                padding=(1, 3),
                expand=False,
            )
        )

        return {
            "city": city,
            "condition": description,
            "temperature": temp,
            "feels_like": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind_speed": current["wind_speed_10m"],
            "time": time,
        }

    def show_forecast(self, weather):
        daily = weather["daily"]

        table = Table(title="5-DAY WEATHER FORECAST", show_lines=True, border_style="cyan")
        table.add_column("Date", style="bold")
        table.add_column("Condition")
        table.add_column("Max", justify="right")
        table.add_column("Min", justify="right")
        table.add_column("Rain Chance", justify="right")

        for i, date in enumerate(daily["time"]):
            description, icon = WEATHER_CODES.get(daily["weather_code"][i], UNKNOWN_WEATHER)
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]

            table.add_row(
                date,
                f"{icon} {description}",
                f"[{temp_color(max_temp)}]{max_temp} °C[/]",
                f"[{temp_color(min_temp)}]{min_temp} °C[/]",
                f"{daily['precipitation_probability_max'][i]}%",
            )

        console.print(table)

    
    def show_weather(self):
        while True:
            city = console.input(
                "[bold cyan]Enter city name (or type 'back' to return):[/] "
            ).strip()

            if city.lower() == "back":
                info("Returning to the main menu.")
                return None

            if not city:
                error("City name cannot be empty!")
                continue

            if len(city) < 3:
                error("Invalid city name! Please enter a valid city.")
                continue

            try:
                with console.status(
                    "[cyan]Fetching weather and forecast...[/]",
                    spinner="dots"
                ):
                    location = self.get_location(city)

                    if location is None:
                        error(
                            "City not found! Enter a valid city "
                            "or type 'back' to return to the menu."
                        )
                        continue

                    weather = self.get_weather(location)

                section("CURRENT WEATHER", "blue")
                summary = self.show_current_weather(location, weather)

                console.print()
                self.show_forecast(weather)

                return summary

            except requests.exceptions.RequestException:
                error("Weather service unavailable. Please try again.")
                continue

            except (KeyError, IndexError, TypeError, ValueError):
                error("Could not read the weather data. Please try again.")
                continue

