"""VOX Cinema Booking - start the program with:  python main.py"""

from colorama import init

from cinema.config.settings import APP_NAME
from cinema.screens.booking_screen import new_booking
from cinema.screens.help_screen import show_help
from cinema.screens.insights_screen import show_recommendations, show_statistics
from cinema.screens.my_bookings_screen import my_bookings_menu
from cinema.storage.bookings_file import ensure_folders
from cinema.ui.display import clear_screen, print_title
from cinema.ui.inputs import ask_menu

MAIN_MENU = [
    "Book a ticket",
    "My bookings (view / change seats / cancel)",
    "Recommendations for me",
    "Cinema statistics",
    "How to use",
    "Exit",
]


def run() -> None:
    ensure_folders()
    while True:
        clear_screen()
        print_title(f"🎬  {APP_NAME}  🎬")
        print()
        choice = ask_menu(MAIN_MENU)
        if choice in (1, 2, 3, 4, 5):
            try:
                if choice == 1:
                    new_booking()
                elif choice == 2:
                    my_bookings_menu()
                elif choice == 3:
                    show_recommendations()
                elif choice == 4:
                    show_statistics()
                else:
                    show_help()
            except ValueError as error:
                print(f"\nData error: {error}")
                input("Press Enter to return to the menu...")
            except OSError as error:
                print(f"\nFile error: {error}")
                input("Press Enter to return to the menu...")
        elif choice == 6:
            break


def main() -> None:
    init()  # makes colors work on Windows too
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram closed by the user.")
    finally:
        print("Thank you for choosing VOX Cinemas. See you soon! 🍿")


if __name__ == "__main__":
    main()
