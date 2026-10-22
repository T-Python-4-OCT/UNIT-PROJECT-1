import time
import os

from countries import CONTINENTS, COUNTRIES
from weather import show_weather
from currency import get_currency
from holiday_calendar import show_holidays
from recommendations import find_my_destination
from language import choose_language

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


def clear_screen():
    os.system("cls")


def show_welcome(language):
    if language == "ar":
        title = "اكتشف العالم"
    else:
        title = "TRAVEL EXPLORER"

    # Animate the airplane
    for position in range(70, 5, -3):
        clear_screen()

        print("\n" * 2)

        print(" " * position + "☁️")
        print()

        print(" " * position + "✈️")
        print()

        print(
            " " * 25
            + "🌍 "
            + title
            + " 🌍"
        )

        time.sleep(0.08)

    clear_screen()

    print("\n")

    print(
        CYAN
        + "              ████████╗██████╗  █████╗ ██╗   ██╗███████╗██╗     "
        + RESET
    )

    print(
        CYAN
        + "              ╚══██╔══╝██╔══██╗██╔══██╗██║   ██║██╔════╝██║     "
        + RESET
    )

    print(
        CYAN
        + "                 ██║   ██████╔╝███████║██║   ██║█████╗  ██║     "
        + RESET
    )

    print(
        CYAN
        + "                 ██║   ██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║     "
        + RESET
    )

    print(
        CYAN
        + "                 ██║   ██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗"
        + RESET
    )

    print()

    print(
        GREEN
        + "                    🌍  E X P L O R E R  🌍"
        + RESET
    )

    print()

    print(
        YELLOW
        + "              ✈️  DISCOVER  •  EXPLORE  •  TRAVEL  ✈️"
        + RESET
    )

    print()

    print(
        BLUE
        + "                    Preparing your journey"
        + RESET,
        end=""
    )

    for _ in range(4):
        time.sleep(0.3)
        print(".", end="", flush=True)

    print("\n")

    print(
        CYAN
        + "                    ☁️        ✈️        ☁️"
        + RESET
    )

    print()

    time.sleep(0.5)


def show_menu(language):
    print()

    if language == "ar":
        title = "اكتشف العالم"
        option_1 = "استكشف دولة"
        option_2 = "اعثر على وجهتي"
        option_3 = "المفضلة"
        option_4 = "خروج"
    else:
        title = "TRAVEL EXPLORER"
        option_1 = "Explore a Country"
        option_2 = "Find My Destination"
        option_3 = "Favorites"
        option_4 = "Exit"

    print(
        CYAN
        + "╔══════════════════════════════════════╗"
        + RESET
    )

    print(
        CYAN
        + f"║          🌍 {title}"
        + RESET
    )

    print(
        CYAN
        + "╠══════════════════════════════════════╣"
        + RESET
    )

    print(
        f"║  1. 🔎 {option_1}"
    )

    print(
        f"║  2. 🤖 {option_2}"
    )

    print(
        f"║  3. ❤️  {option_3}"
    )

    print(
        f"║  4. 🚪 {option_4}"
    )

    print(
        CYAN
        + "╚══════════════════════════════════════╝"
        + RESET
    )


def choose_menu_option(language):
    show_menu(language)

    while True:
        choice = input(
            YELLOW
            + "\n👉 Choose an option: "
            + RESET
        )

        if choice in ["1", "2", "3", "4"]:
            return choice

        print(
            RED
            + "❌ Invalid choice. Please choose 1-4."
            + RESET
        )


def show_continents(language):
    print(
        CYAN
        + "🌍 Choose a continent:"
        + RESET
    )

    print()

    for number, continent in CONTINENTS.items():

        if language == "ar":
            name = continent["name_ar"]
        else:
            name = continent["name"]

        print(
            f"{number}. "
            f"{continent['emoji']} "
            f"{name}"
        )


def choose_continent(language):
    show_continents(language)

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


def show_countries(countries, language):
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


def choose_country(countries, language):
    show_countries(
        countries,
        language
    )

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


def explore_country(language):
    loading("🚀 Starting your journey")

    continent = choose_continent(language)

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

    country_name = choose_country(
        countries,
        language
    )

    city = choose_city(
        country_name
    )

    show_destination(
        country_name,
        city
    )

    print()

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


def find_destination():
    find_my_destination()


def show_favorites():
    print()

    print(
        MAGENTA
        + "❤️ Favorites"
        + RESET
    )

    print()

    print(
        YELLOW
        + "🚧 This feature is coming soon."
        + RESET
    )


def main():
    language = choose_language()

    show_welcome(language)

    while True:

        choice = choose_menu_option(
            language
        )

        if choice == "1":

            clear_screen()

            explore_country(
                language
            )

        elif choice == "2":

            clear_screen()

            find_destination()

        elif choice == "3":

            clear_screen()

            show_favorites()

        elif choice == "4":

            print()

            if language == "ar":

                print(
                    GREEN
                    + "✈️ شكرًا لاستخدامك اكتشف العالم!"
                    + RESET
                )

                print(
                    CYAN
                    + "🌍 نراك في رحلتك القادمة!"
                    + RESET
                )

            else:

                print(
                    GREEN
                    + "✈️ Thank you for using Travel Explorer!"
                    + RESET
                )

                print(
                    CYAN
                    + "🌍 See you on your next journey!"
                    + RESET
                )

            break

        input(
            "\nPress Enter to return to the main menu..."
        )

        clear_screen()


if __name__ == "__main__":
    main()