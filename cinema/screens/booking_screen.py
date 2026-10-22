"""The full 'Book a ticket' journey: name -> cinema -> movie -> experience -> showtime -> seats -> confirm."""

import random

from cinema.models.booking import Booking, make_show_key
from cinema.models.hall import Hall
from cinema.screens.choosers import choose_branch, choose_hall, choose_movie, choose_show_time, format_date
from cinema.screens.seat_picker import calculate_total, select_seats
from cinema.ui.display import clear_screen, print_info, print_success, print_title
from cinema.ui.inputs import ask_name, ask_yes_no


def print_summary(customer: str, branch: str, movie: dict, hall: Hall,
                  show_date: str, show_time: str, seats: list[str]) -> None:
    print(f"Customer      : {customer}")
    print(f"Cinema        : {branch}")
    print(f"Movie         : {movie['title']} ({movie['year']})")
    print(f"Experience    : {hall.name}")
    print(f"Your showtime : {format_date(show_date)} at {show_time}")
    print("-" * 40)
    for seat in seats:
        print(f"  Seat {seat:<4} {hall.seat_type(seat):<9} {hall.seat_price(seat):>6.0f} SAR")
    print("-" * 40)
    print(f"  TOTAL ({len(seats)} seats)      {calculate_total(hall, seats):>6.0f} SAR")


def new_booking() -> None:
    clear_screen()
    print_title("Your name")
    customer = ask_name()

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
    show_key = make_show_key(branch, movie["title"], hall.name, show_date, show_time)
    taken = hall.taken_by_others(show_key)
    seats = select_seats(hall, taken)

    clear_screen()
    print_title("Booking summary")
    print_summary(customer, branch, movie, hall, show_date, show_time, seats)
    print()
    if ask_yes_no("Confirm this booking?"):
        invoice = random.randint(10000, 99999)
        booking = Booking(invoice, customer, branch, movie["title"], movie["genre"],
                          hall.name, show_date, show_time, seats, calculate_total(hall, seats))
        print()
        print_success(f"Booking confirmed! Keep your invoice number: {booking.invoice}")
        print()
        booking.print_ticket()
    else:
        print_info("Booking cancelled.")
    input("\nPress Enter to return to the main menu...")
