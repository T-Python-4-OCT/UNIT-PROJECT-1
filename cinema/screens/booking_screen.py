"""The 'Book a ticket' journey (still under construction)."""

from cinema.screens.choosers import choose_branch, choose_hall, choose_movie, choose_show_time, format_date
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
    print_title("Choose your showtime")
    show_date, show_time = choose_show_time()

    clear_screen()
    print_title(f"{movie['title']} - {hall.name} - {format_date(show_date)} {show_time}")
    show_key = f"{branch}|{movie['title']}|{hall.name}|{show_date}|{show_time}"
    taken = hall.taken_by_others(show_key)
    seats = select_seats(hall, taken)

    print()
    print_success(f"Your seats: {', '.join(seats)} - Total: {calculate_total(hall, seats):.0f} SAR")
    input("\nPress Enter to return to the main menu...")
