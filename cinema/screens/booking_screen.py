"""The 'Book a ticket' journey (still under construction)."""

from cinema.screens.choosers import choose_branch, choose_hall, choose_movie
from cinema.screens.seat_picker import calculate_total, select_seats
from cinema.ui.display import clear_screen, print_success, print_title


def new_booking() -> None:
    clear_screen()
    print_title("Choose a cinema")
    branch = choose_branch()

    clear_screen()
    print_title(f"Movies at {branch}")
    movie = choose_movie(branch)

    clear_screen()
    print_title("Choose your experience")
    hall = choose_hall()

    clear_screen()
    print_title(f"{movie['title']} - {hall.name}")
    show_key = f"{branch}|{movie['title']}|{hall.name}"
    taken = hall.taken_by_others(show_key)
    seats = select_seats(hall, taken)

    print()
    print_success(f"Your seats: {', '.join(seats)} - Total: {calculate_total(hall, seats):.0f} SAR")
    input("\nPress Enter to return to the main menu...")
