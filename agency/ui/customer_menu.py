
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import countries
from agency.ui import views
from agency.ui.console import GoBack, ask_choice, console, error, info, pause

MENU = [
    ("1", "Browse destinations"),
    ("0", "Logout"),
]


def run(user: User) -> None:
    actions = {
        "1": browse,
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
