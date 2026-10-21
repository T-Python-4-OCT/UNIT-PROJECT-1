"""The 'Book a ticket' journey (still under construction)."""

from cinema.screens.choosers import choose_branch, choose_hall, choose_movie
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

    print()
    print_success(f"You chose {movie['title']} in {hall.name} at {branch}.")
    input("\nPress Enter to return to the main menu...")
