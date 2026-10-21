import time

from countries import CONTINENTS, COUNTRIES
from weather import show_weather
from currency import get_currency
from holiday_calendar import show_holidays
from budget import show_budget


BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
RESET = "\033[0m"


def loading(message):
    print(CYAN + message + RESET, end="")

    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)

    print()


def show_welcome():
    print()
    print(
        CYAN
        + "╔══════════════════════════════════════╗"
        + RESET
    )

    print(
        BLUE
        + "║       🌍✈️ TRAVEL ASSISTANT ✈️🌍    ║"
        + RESET
    )

    print(
        CYAN
        + "╠══════════════════════════════════════╣"
        + RESET
    )

    print(
        GREEN
        + "║       🧳 Smart Travel Guide         ║"
        + RESET
    )

    print(
        YELLOW
        + "║       🌤️ Live Weather               ║"
        + RESET
    )

    print(
        MAGENTA
        + "║       💰 Budget Planning            ║"
        + RESET
    )

    print(
        BLUE
        + "║       📅 Travel Calendar            ║"
        + RESET
    )

    print(
        CYAN
        + "╚══════════════════════════════════════╝"
        + RESET
    )

    print()


def show_continents():
    print(
        CYAN
        + "🌍 Choose a continent:"
        + RESET
    )

    print()

    for number, continent in CONTINENTS.items():
        print(
            f"{number}. "
            f"{continent['emoji']} "
            f"{continent['name']}"
        )


def choose_continent():
    show_continents()

    while True:
        choice = input(
            YELLOW
            + "\n👉 Choose: "
            + RESET
        )

        if choice in CONTINENTS:
            return CONTINENTS[choice]

        print(
            RED
            + "❌ Invalid choice. Choose 1-5."
            + RESET
        )


def get_countries(continent_name):
    countries = []

    for country_name, country in COUNTRIES.items():
        if country["continent"] == continent_name:
            countries.append(country_name)

    return countries


def show_countries(countries):
    print()
    print(
        CYAN
        + "🌍 Available countries:"
        + RESET
    )

    print()

    for number, country_name in enumerate(
        countries,
        start=1
    ):
        country = COUNTRIES[country_name]

        print(
            f"{number}. "
            f"{country['flag']} "
            f"{country_name}"
        )


def choose_country(countries):
    show_countries(countries)

    while True:
        choice = input(
            YELLOW
            + "\n👉 Choose a country: "
            + RESET
        )

        try:
            number = int(choice)

            if 1 <= number <= len(countries):
                return countries[number - 1]

            print(
                RED
                + "❌ Number is out of range."
                + RESET
            )

        except ValueError:
            print(
                RED
                + "❌ Please enter a number."
                + RESET
            )


def show_cities(country_name):
    country = COUNTRIES[country_name]

    print()

    print(
        CYAN
        + f"{country['flag']} "
        f"{country_name} - Cities:"
        + RESET
    )

    print()

    for number, city in country["cities"].items():
        print(
            f"{number}. "
            f"📍 {city['name']}"
        )


def choose_city(country_name):
    country = COUNTRIES[country_name]

    show_cities(country_name)

    while True:
        choice = input(
            YELLOW
            + "\n👉 Choose a city: "
            + RESET
        )

        if choice in country["cities"]:
            return country["cities"][choice]

        print(
            RED
            + "❌ Invalid city choice."
            + RESET
        )


def show_destination(country_name, city):
    country = COUNTRIES[country_name]
    currency = get_currency(country_name)

    print()

    print(
        GREEN
        + "╔══════════════════════════════════════╗"
        + RESET
    )

    print(
        GREEN
        + f"║ {country['flag']} {country_name}"
        + RESET
    )

    print(
        CYAN
        + f"║ 📍 {city['name']}"
        + RESET
    )

    if currency:
        print(
            YELLOW
            + f"║ 💰 Currency: {currency['name']} "
            f"({currency['code']})"
            + RESET
        )

    print(
        GREEN
        + "╚══════════════════════════════════════╝"
        + RESET
    )


def main():
    show_welcome()

    loading("🚀 Starting your journey")

    continent = choose_continent()

    print()

    print(
        GREEN
        + f"✅ {continent['emoji']} "
        + continent["name"]
        + RESET
    )

    countries = get_countries(
        continent["name"]
    )

    if not countries:
        print(
            RED
            + "❌ No countries available yet."
            + RESET
        )
        return

    country_name = choose_country(countries)

    city = choose_city(country_name)

    show_destination(
        country_name,
        city
    )

    print()

    show_budget()

    loading(
        "🌤️ Getting live weather data"
    )

    show_weather(city)

    show_holidays(country_name)

    print()

    print(
        MAGENTA
        + "🎉 Destination analysis completed!"
        + RESET
    )


if __name__ == "__main__":
    main()