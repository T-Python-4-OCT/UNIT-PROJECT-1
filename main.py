"""VOX Cinema Booking - start the program with:  python main.py"""

from colorama import init

from cinema.config.settings import APP_NAME
from cinema.screens.booking_screen import new_booking
from cinema.screens.my_bookings_screen import my_bookings_menu
from cinema.storage.bookings_file import ensure_folders
from cinema.ui.decorators import pause_after
from cinema.ui.display import clear_screen, print_info, print_title
from cinema.ui.inputs import ask_menu

MAIN_MENU = [
    "Book a ticket",
    "My bookings (view / change seats / cancel)",
    "Recommendations for me",
    "Cinema statistics",
    "How to use",
    "Exit",
]


@pause_after
def show_coming_soon() -> None:
    print_info("This feature is coming soon...")


def run() -> None:
    ensure_folders()
    while True:
        clear_screen()
        print_title(f"🎬  {APP_NAME}  🎬")
        print()
        choice = ask_menu(MAIN_MENU)
        if choice == 1:
            new_booking()
        elif choice == 2:
            my_bookings_menu()
        elif choice == 3:
            show_coming_soon()
        elif choice == 4:
            show_coming_soon()
        elif choice == 5:
            show_coming_soon()
        elif choice == 6:
            break


def main() -> None:
    init()  # makes colors work on Windows too
    run()
    print("Thank you for choosing VOX Cinemas. See you soon! 🍿")


if __name__ == "__main__":
    main()
