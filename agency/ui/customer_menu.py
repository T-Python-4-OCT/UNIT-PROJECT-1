
from agency.config import (CURRENCY, DEFAULT_DAYS, GROUP_DISCOUNT_PERCENT, GROUP_SIZE, MAX_DAYS,
                           MIN_DAYS)
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import countries, planner, weather
from agency.ui import views
from agency.ui.console import (GoBack, ask_choice, ask_int, ask_text, console, error, info, pause,
                               warn)

MENU = [
    ("1", "Browse destinations"),
    ("2", "View destination details + live weather"),
    ("3", "Search destinations"),
    ("4", "Plan a trip by budget"),
    ("0", "Logout"),
]


def run(user: User) -> None:
    actions = {
        "1": browse,
        "2": details,
        "3": search,
        "4": lambda: plan_trip(user),
    }
    while True:
        console.print()
        views.show_menu(f"Customer menu - {user.full_name}", MENU)
        choice = ask_choice("Choose", [k for k, _ in MENU], allow_back=False)
        if choice == "0":
            info("Logged out. See you soon!")
            return
        try:
            actions[choice]()
        except GoBack:
            info("Cancelled. Back to the menu.")
            continue
        except ServiceError as exc:
            error(str(exc))
        pause()


def browse() -> None:
    views.show_countries(countries.list_all(), "All destinations")


def details() -> None:
    browse()
    _show_destination_report(countries.get(ask_int("Destination ID", minimum=1)))


def _show_destination_report(destination) -> None:
    views.show_country_detail(destination)
    _show_live_weather(destination)


def _show_live_weather(destination) -> None:
    try:
        with console.status("[cyan]Fetching live weather...[/cyan]"):
            report = weather.get_forecast(destination)
    except ServiceError as exc:
        warn(str(exc))
        return
    views.show_weather(report)


def search() -> None:
    field = ask_choice("Search by", ["country", "city", "type"])
    if field == "type":
        query = ask_choice("Trip type", countries.CATEGORIES)
        results, corrected = countries.search_by("category", query)
    else:
        query = ask_text(f"Enter the {field} name")
        results, corrected = countries.search_by(field, query)
    if not results:
        warn(f"No destinations match '{query}'.")
        return
    if corrected:
        warn(f"No exact match for '{query}'. Showing the closest spelling instead.")
    views.show_countries(results, f"Results for '{query}'")
    _offer_details(results)


def _offer_details(results) -> None:
    listed_ids = {destination.id for destination in results}
    while True:
        chosen = ask_int("Enter an ID to see its details and live weather (0 to skip)", minimum=0)
        if chosen == 0:
            return
        if chosen in listed_ids:
            break
        error("Please choose one of the IDs shown in the table above.")
    _show_destination_report(countries.get(chosen))


def _ask_days() -> int:
    info(f"{DEFAULT_DAYS} days is a good trip: press Enter to accept it, or choose what suits you.")
    return ask_int("Number of days", minimum=MIN_DAYS, maximum=MAX_DAYS, default=DEFAULT_DAYS)


def _ask_trip_options():
    days = _ask_days()
    info(f"Special offer: if you are {GROUP_SIZE} travelers you get {GROUP_DISCOUNT_PERCENT}% off!")
    travelers = ask_int("Number of travelers", minimum=1, maximum=20, default=1)
    style = ask_choice("Travel style", list(planner.STYLES), default="standard")
    return days, travelers, style


def plan_trip(user: User) -> None:
    budget = ask_int(f"Your total budget ({CURRENCY})", minimum=1)
    days, travelers, style = _ask_trip_options()
    category = ask_choice("Trip type", ["any", *countries.CATEGORIES], default="any")

    matches, cheapest = planner.find_matches(
        budget, days, travelers, style, "" if category == "any" else category)

    if not matches:
        destination, cost = cheapest
        error("Your budget is not enough for this trip.")
        info(f"Cheapest option: {views.place(destination)} = {views.money(cost['Total'])}")
        warn(f"You need {views.money(cost['Total'] - budget)} more, "
             "or try fewer days / economy style.")
        return

    views.show_plan_options(matches, budget)
    pick = ask_int("Pick a number for the full plan (0 to go back)",
                   minimum=0, maximum=len(matches))
    if pick == 0:
        return
    destination, cost = matches[pick - 1]
    _show_destination_report(destination)
    views.show_itinerary(destination, days)
    views.show_breakdown(cost, budget=budget)
    info("Prices are estimates.")
