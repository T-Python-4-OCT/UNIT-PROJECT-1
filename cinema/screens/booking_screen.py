"""The full 'Book a ticket' journey: name -> cinema -> movie -> experience -> showtime -> seats -> confirm."""

from cinema.models.booking import Booking, make_show_key
from cinema.models.hall import Hall
from cinema.screens.choosers import choose_branch, choose_hall, choose_movie, choose_show_time, format_date
from cinema.screens.seat_picker import calculate_total, select_seats
from cinema.storage.bookings_file import load_bookings, save_bookings
from cinema.storage.search import booked_seats, new_invoice_number
from cinema.storage.tickets import export_ticket
from cinema.ui.decorators import pause_after
from cinema.ui.display import print_error, print_info, print_step, print_success
from cinema.ui.inputs import ask_name, ask_yes_no

TOTAL_STEPS = 7


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


def finish_booking(booking: Booking) -> None:
    """Show the ticket and offer to save the ticket file."""
    print()
    print_success(f"Booking confirmed! Keep your invoice number: {booking.invoice}")
    print()
    booking.print_ticket()
    print()
    if ask_yes_no("Save the ticket as a text file?"):
        path = export_ticket(booking)
        print_success(f"Ticket saved to {path}")


@pause_after
def new_booking() -> None:
    print_step(1, TOTAL_STEPS, "Your name")
    customer = ask_name()

    print_step(2, TOTAL_STEPS, "Choose a cinema")
    branch = choose_branch()

    print_step(3, TOTAL_STEPS, f"Movies at {branch}")
    movie = choose_movie(branch)

    print_step(4, TOTAL_STEPS, "Choose your experience")
    hall = choose_hall()

    print_step(5, TOTAL_STEPS, "Choose your showtime")
    show_date, show_time = choose_show_time()

    bookings = load_bookings()
    show_key = make_show_key(branch, movie["title"], hall.name, show_date, show_time)
    taken = hall.taken_by_others(show_key) | booked_seats(bookings, show_key)  # set union
    if len(taken) >= hall.capacity():
        print_error("Sorry, this show is sold out.")
        return

    print_step(6, TOTAL_STEPS, f"{movie['title']} - {hall.name} - {format_date(show_date)} {show_time}")
    seats = select_seats(hall, taken)
    if not seats:
        print_info("No seats were chosen. Booking cancelled.")
        return

    print_step(7, TOTAL_STEPS, "Booking summary")
    print_summary(customer, branch, movie, hall, show_date, show_time, seats)
    print()
    if not ask_yes_no("Confirm this booking?"):
        print_info("Booking cancelled. Nothing was saved.")
        return

    booking = Booking(new_invoice_number(bookings), customer, branch, movie["title"], movie["genre"],
                      hall.name, show_date, show_time, seats, calculate_total(hall, seats))
    bookings.append(booking)
    if not save_bookings(bookings):
        print_error("Could not save the booking. Please try again.")
        return
    finish_booking(booking)
