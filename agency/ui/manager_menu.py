from agency.errors import ServiceError
from agency.models.user import User
from agency.services import countries
from agency.ui import views
from agency.ui.console import GoBack, ask_choice, console, error, info, pause

MENU = [
    ("6", "List destinations"),
    ("0", "Logout"),
]


def run(user: User) -> None:
    actions = {
        "6": list_destinations,
    }
    while True:
        console.print()
        views.show_menu(f"Manager menu - {user.full_name}", MENU, "magenta")

        choice = ask_choice("Choose", [k for k, _ in MENU], allow_back=False)
        if choice == "0":
            info("Logged out.")
            return
        try:
            actions[choice]()
        except GoBack:
            info("Cancelled. Back to the menu.")
            continue
        except ServiceError as exc:
            error(str(exc))
        pause()


def list_destinations() -> None:
    views.show_countries(countries.list_all(), "All destinations")
