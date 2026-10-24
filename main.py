
import os
import time

from countries import CONTINENTS, COUNTRIES
from weather import show_weather
from currency import show_currency
from holiday_calendar import show_holidays
from recommendations import find_my_destination
from favorites import (
    add_favorite,
    remove_favorite,
    show_favorites,
    is_favorite,
)
from destination_info import show_destination_info


# ============================================================
# COLORS
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"


# ============================================================
# SCREEN
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n{CYAN}Press Enter to continue...{RESET}")


# ============================================================
# INTRO
# ============================================================

def show_logo():
    clear_screen()

    print(CYAN + r"""
 ████████╗██████╗  █████╗ ██╗   ██╗███████╗██╗     
 ╚══██╔══╝██╔══██╗██╔══██╗██║   ██║██╔════╝██║     
    ██║   ██████╔╝███████║██║   ██║█████╗  ██║     
    ██║   ██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║     
    ██║   ██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗
    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝

 ███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██████╗ ███████╗██████╗
 ██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝██╔══██╗
 █████╗   ╚███╔╝ ██████╔╝██║     ██║   ██║██████╔╝█████╗  ██████╔╝
 ██╔══╝   ██╔██╗ ██╔══██╗██║     ██║   ██║██╔══██╗██╔══╝  ██╔══██╗
 ███████╗██╔╝ ██╗██████╔╝███████╗╚██████╔╝██║  ██║███████╗██║  ██║
 ╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
""" + RESET)

    print(
        BOLD + WHITE +
        "                    ✈  DISCOVER THE WORLD  ✈"
        + RESET
    )

    print()
    print(BLUE + "              ─────────────────────────────────" + RESET)
    print()


def airplane_animation():
    print()

    frames = [
        "✈",
        "  ✈",
        "    ✈",
        "      ✈",
        "        ✈",
        "          ✈",
        "            ✈",
    ]

    for frame in frames:
        print("\r" + CYAN + frame + "  ☁️   ☁️   ☁️" + RESET, end="")
        time.sleep(0.12)

    print()


def loading_animation():
    print()

    print(
        YELLOW +
        "Initializing your journey"
        + RESET,
        end="",
    )

    for _ in range(4):
        time.sleep(0.35)
        print(".", end="", flush=True)

    print()

    print(
        GREEN +
        "✓ Travel Explorer is ready!"
        + RESET
    )

    time.sleep(0.7)


def intro():
    show_logo()
    airplane_animation()
    loading_animation()

    print()
    print(
        WHITE +
        "Explore countries • Check live weather • Discover food"
        + RESET
    )
    print(
        WHITE +
        "Find famous places • Check holidays • Get smart recommendations"
        + RESET
    )

    print()
    pause()


# ============================================================
# UI HELPERS
# ============================================================

def print_header(title):
    clear_screen()

    print()
    print(
        CYAN +
        "╔" + "═" * 68 + "╗"
        + RESET
    )

    print(
        CYAN +
        "║"
        + RESET
        + BOLD
        + WHITE
        + f"{title:^68}"
        + RESET
        + CYAN
        + "║"
        + RESET
    )

    print(
        CYAN +
        "╚" + "═" * 68 + "╝"
        + RESET
    )

    print()


def print_menu_option(number, icon, title, description):
    print(
        f"  {YELLOW}{number}{RESET}  "
        f"{CYAN}{icon}{RESET} "
        f"{BOLD}{WHITE}{title}{RESET}"
    )

    print(
        f"      {description}"
    )

    print()


# ============================================================
# COUNTRY SELECTION
# ============================================================

def choose_continent():
    print_header("🌍 CHOOSE YOUR CONTINENT")

    continent_list = list(CONTINENTS.values())

    for index, continent in enumerate(
        continent_list,
        start=1,
    ):
        print(
            f"  {YELLOW}{index}{RESET}. "
            f"{continent['emoji']} "
            f"{continent['name']}"
        )

    print()
    print(f"  {YELLOW}0{RESET}. ↩️ Back")

    while True:
        choice = input(
            f"{CYAN}➜ Select a continent: {RESET}"
        ).strip()

        if choice.isdigit():
            number = int(choice)

            if number == 0:
             return None
            if 1 <= number <= len(continent_list):
                return continent_list[number - 1]

        print(
            RED +
            "❌ Invalid choice. Please try again."
            + RESET
        )


def choose_country(continent):
    countries = []

    for country_name, country_data in COUNTRIES.items():
        if country_data["continent"] == continent["name"]:
            country_data["name"] = country_name
            countries.append(country_data)

    if not countries:
        print(
            RED +
            "❌ No countries found."
            + RESET
        )
        return None

    print_header(
        f"🌎 {continent['name'].upper()}"
    )

    for index, country in enumerate(
        countries,
        start=1,
    ):
        print(
            f"  {YELLOW}{index:02d}{RESET}. "
            f"{country['flag']} "
            f"{country['name']}"
        )

    print()
    print(f"  {YELLOW}0{RESET}. ↩️ Back")

    while True:
        choice = input(
            f"{CYAN}➜ Select a country: {RESET}"
        ).strip()

        if choice.isdigit():
            number = int(choice)
            
            if number == 0:
                return None

            if 1 <= number <= len(countries):
                return countries[number - 1]

        print(
            RED +
            "❌ Invalid choice. Please try again."
            + RESET
        )


def choose_city(country):
    cities = list(country.get("cities", {}).values())

    if not cities:
        return None

    print_header(
        f"🏙️ CITIES OF {country['name'].upper()}"
    )

    for index, city in enumerate(
        cities,
        start=1,
    ):
        print(
            f"  {YELLOW}{index}{RESET}. "
            f"{city['name']}"
        )

    print()

    while True:
        choice = input(
            f"{CYAN}➜ Select a city: {RESET}"
        ).strip()

        if choice.isdigit():
            number = int(choice)

            if 1 <= number <= len(cities):
                return cities[number - 1]

        print(
            RED +
            "❌ Invalid city."
            + RESET
        )


# ============================================================
# COUNTRY EXPLORER
# ============================================================

def explore_country():
    while True:
        continent = choose_continent()

        if not continent:
            return

        while True:
            country = choose_country(continent)

            if not country:
                break

            while True:
                print_header(
                    f"🌍 EXPLORE {country['name'].upper()}"
                )

                print_menu_option(
                    "1",
                    "📖",
                    "Country Information",
                    "Discover what this country is famous for.",
                )

                print_menu_option(
                    "2",
                    "🍣",
                    "Famous Foods",
                    "Explore popular local dishes.",
                )

                print_menu_option(
                    "3",
                    "🎉",
                    "Events & Experiences",
                    "Discover festivals and unique experiences.",
                )

                print_menu_option(
                    "4",
                    "🏯",
                    "Famous Places",
                    "Explore famous cities and attractions.",
                )

                print_menu_option(
                    "5",
                    "🌤️",
                    "Live Weather",
                    "Check current weather conditions.",
                )

                print_menu_option(
                    "6",
                    "💰",
                    "Currency",
                    "Check currency and live exchange rate.",
                )

                print_menu_option(
                    "7",
                    "📅",
                    "Holidays",
                    "View public holidays for 2026.",
                )

                print_menu_option(
                    "8",
                    "⭐",
                    "Add to Favorites",
                    "Save this country for later.",
                )

                print_menu_option(
                    "9",
                    "🗑️",
                    "Remove from Favorites",
                    "Remove this country from your favorites.",
                )

                print_menu_option(
                    "0",
                    "↩️",
                    "Back",
                    "Return to the country list.",
                )

                choice = input(
                    f"{CYAN}➜ Choose an option: {RESET}"
                ).strip()

                if choice == "1":
                    clear_screen()
                    show_destination_info(
                        country["name"]
                    )
                    pause()

                elif choice == "2":
                    clear_screen()
                    show_destination_info(
                        country["name"],
                        section="foods",
                    )
                    pause()

                elif choice == "3":
                    clear_screen()
                    show_destination_info(
                        country["name"],
                        section="events",
                    )
                    pause()

                elif choice == "4":
                    clear_screen()
                    show_destination_info(
                        country["name"],
                        section="places",
                    )
                    pause()

                elif choice == "5":
                    city = choose_city(country)

                    if city:
                        clear_screen()
                        show_weather(city)
                        pause()

                elif choice == "6":
                    clear_screen()
                    show_currency(country["name"])
                    pause()

                elif choice == "7":
                    clear_screen()
                    show_holidays(country["name"])
                    pause()

                elif choice == "8":
                    clear_screen()

                    if is_favorite(country["name"]):
                        print(
                            YELLOW +
                            "⭐ This country is already in your favorites."
                            + RESET
                        )
                    else:
                        add_favorite(country["name"])

                        print(
                            GREEN +
                            f"✓ {country['name']} added to favorites!"
                            + RESET
                        )

                    pause()

                elif choice == "9":
                    clear_screen()

                    if is_favorite(country["name"]):
                        remove_favorite(country["name"])

                        print(
                            GREEN +
                            f"✓ {country['name']} removed from favorites."
                            + RESET
                        )
                    else:
                        print(
                            YELLOW +
                            "ℹ This country is not in your favorites."
                            + RESET
                        )

                    pause()

                elif choice == "0":
                    break

                else:
                    print(
                        RED +
                        "❌ Invalid option."
                        + RESET
                    )

                    time.sleep(1)
# ============================================================
# FAVORITES
# ============================================================

def favorites_menu():
    while True:
        print_header("⭐ MY FAVORITES")

        favorites = show_favorites(
            return_data=True
        )

        if not favorites:
            print(
                YELLOW +
                "You don't have any favorite countries yet."
                + RESET
            )

            print()
            print(
                "Go to Explore a Country and save your favorite destinations."
            )

            print()

        else:
            print(
                BOLD +
                WHITE +
                "Your Saved Destinations:"
                + RESET
            )

            print()

            for index, country_name in enumerate(
                favorites,
                start=1,
            ):
                print(
                    f"  {YELLOW}{index}{RESET}. "
                    f"⭐ {country_name}"
                )

            print()

        print(
            f"  {YELLOW}1{RESET}. 🗑️ Remove a Favorite"
        )

        print(
            f"  {YELLOW}0{RESET}. ↩️ Back"
        )

        print()

        choice = input(
            f"{CYAN}➜ Choose an option: {RESET}"
        ).strip()

        if choice == "1":

            if favorites:
                remove_favorite_menu(
                    favorites
                )
            else:
                print(
                    YELLOW +
                    "No favorites to remove."
                    + RESET
                )
                pause()

        elif choice == "0":
            break

        else:
            print(
                RED +
                "❌ Invalid option."
                + RESET
            )


def remove_favorite_menu(favorites):
    print_header("🗑️ REMOVE FAVORITE")

    for index, country_name in enumerate(
        favorites,
        start=1,
    ):
        print(
            f"  {YELLOW}{index}{RESET}. "
            f"{country_name}"
        )

    print()

    choice = input(
        f"{CYAN}➜ Enter the number: {RESET}"
    ).strip()

    if not choice.isdigit():
        print(
            RED +
            "❌ Please enter a number."
            + RESET
        )
        pause()
        return

    number = int(choice)

    if not 1 <= number <= len(favorites):
        print(
            RED +
            "❌ Invalid number."
            + RESET
        )
        pause()
        return

    country_name = favorites[number - 1]

    remove_favorite(country_name)

    print()
    print(
        GREEN +
        f"✓ {country_name} removed from favorites."
        + RESET
    )

    pause()


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():

    while True:

        print_header("✈️ TRAVEL EXPLORER")

        print_menu_option(
            "1",
            "🌍",
            "Explore a Country",
            "Discover countries, food, places, weather and more.",
        )

        print_menu_option(
            "2",
            "🧠",
            "Find My Destination",
            "Get a smart destination recommendation.",
        )

        print_menu_option(
            "3",
            "⭐",
            "Favorites",
            "View and manage your saved destinations.",
        )

        print_menu_option(
            "4",
            "🚪",
            "Exit",
            "End your journey.",
        )

        choice = input(
            f"{CYAN}➜ Choose an option: {RESET}"
        ).strip()

        if choice == "1":
            explore_country()

        elif choice == "2":
            clear_screen()
            find_my_destination()
            pause()

        elif choice == "3":
            favorites_menu()

        elif choice == "4":
            clear_screen()

            print()
            print(
                CYAN +
                "✈️  THANK YOU FOR USING TRAVEL EXPLORER"
                + RESET
            )

            print()
            print(
                WHITE +
                "Your next adventure is waiting..."
                + RESET
            )

            print()
            print(
                GREEN +
                "🌍 See you on your next journey!"
                + RESET
            )

            print()

            break

        else:
            print(
                RED +
                "❌ Invalid option. Please choose 1 - 4."
                + RESET
            )

            time.sleep(1)


# ============================================================
# START
# ============================================================

def main():
    intro()
    main_menu()


if __name__ == "__main__":
    main()
