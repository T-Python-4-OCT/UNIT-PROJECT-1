"""VOX Cinema Booking - start the program with:  python main.py"""

from colorama import init

from cinema.config.settings import APP_NAME
from cinema.screens.booking_screen import new_booking
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


def show_coming_soon() -> None:
    print_info("This feature is coming soon...")
    input("\nPress Enter to return to the main menu...")


def run() -> None:
    while True:
        clear_screen()
        print_title(f"🎬  {APP_NAME}  🎬")
        print()
        choice = ask_menu(MAIN_MENU)
        if choice == 1:
            new_booking()
        elif choice == 6:
            break
        else:
            show_coming_soon()


def main() -> None:
    init()  # makes colors work on Windows too
    run()
    print("Thank you for choosing VOX Cinemas. See you soon! 🍿")


if __name__ == "__main__":
    main()
