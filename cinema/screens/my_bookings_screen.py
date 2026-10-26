"""'My bookings': find bookings by name or invoice, then view, change seats, cancel or export."""

from datetime import datetime

from cinema.models.booking import Booking
from cinema.models.hall_types import get_hall_by_name
from cinema.screens.seat_picker import calculate_total, select_seats
from cinema.screens.snacks_screen import extras_total
from cinema.storage.bookings_file import load_bookings, save_bookings
from cinema.storage.search import booked_seats, find_by_invoice, find_by_name
from cinema.storage.tickets import export_ticket
from cinema.ui.display import clear_screen, print_error, print_info, print_success, print_title
from cinema.ui.inputs import ask_menu, ask_number, ask_yes_no

ACTIONS = ["View ticket", "Change seats", "Cancel a booking", "Save ticket as text file", "Back to main menu"]


def search_bookings(bookings: list[Booking]) -> list[Booking]:
    while True:
        query = " ".join(input("Enter your full name or invoice number: ").split())
        if not query:
            print_error("Please enter your full name or invoice number.")
            continue
        if query.isdigit():
            booking = find_by_invoice(bookings, int(query))
            return [booking] if booking is not None else []
        if not all(part.isalpha() for part in query.split()):
            print_error("Use letters for a name, or numbers for an invoice.")
            continue
        if len(query.replace(" ", "")) < 3:
            print_error("Please enter at least 3 letters for a name.")
            continue
        return find_by_name(bookings, query)



def print_bookings_table(found: list[Booking]) -> None:
    """Every booking as a small card."""
    for number, booking in enumerate(found, start=1):
        print(f"[{number}] Invoice {booking.invoice}  |  {booking.movie}")
        print(f"    Cinema        : {booking.branch}")
        print(f"    Experience    : {booking.hall}")
        print(f"    Your showtime : {booking.show_date_text()} at {booking.show_time}")
        print(f"    Seats         : {booking.seats_text()}   |   Total (with extras): {booking.total:.0f} SAR")
        print("-" * 60)


def pick_booking(found: list[Booking]) -> Booking:
    if len(found) == 1:
        return found[0]
    number = ask_number("Which booking? (number in [ ]): ", 1, len(found))
    return found[number - 1]


def print_price_difference(old_total: float, new_total: float) -> None:
    difference = new_total - old_total
    if difference > 0:
        print_info(f"Price difference: +{difference:.0f} SAR (simulation, no payment processed).")
    elif difference < 0:
        print_info(f"Price difference: -{abs(difference):.0f} SAR (simulation, no refund processed).")


def show_has_started(booking: Booking) -> bool:
    """Disallow modifications when a show's starting time has passed."""
    try:
        start = datetime.strptime(f"{booking.show_date} {booking.show_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return True  # invalid dates must not allow a change
    return start <= datetime.now()


def change_seats(booking: Booking, bookings: list[Booking]) -> None:
    if show_has_started(booking):
        print_error("This show already started. Seats cannot be changed.")
        return
    hall = get_hall_by_name(booking.hall)
    if hall is None:
        print_error("Unknown hall in this booking.")
        return

    # Your old seats are free again, so they show green on the map
    taken = hall.taken_by_others(booking.show_key()) | booked_seats(bookings, booking.show_key(), booking.invoice)
    print_info(f"Your current seats: {booking.seats_text()} (ticket price {booking.total - extras_total(booking.extras):.0f} SAR). Choose your new seats:")
    new_seats = select_seats(hall, taken)
    if not new_seats:
        print_info("No seats were chosen. Your booking stays the same.")
        return

    new_total = calculate_total(hall, new_seats) + extras_total(booking.extras)
    print()
    print(f"Old seats: {booking.seats_text():<20} {booking.total:.0f} SAR")
    print(f"New seats: {', '.join(new_seats):<20} {new_total:.0f} SAR")
    print_price_difference(booking.total, new_total)

    if ask_yes_no("Save the new seats?"):
        old_seats, old_total = booking.seats, booking.total
        booking.seats = new_seats
        booking.total = new_total
        if save_bookings(bookings):
            print_success("Seats updated.")
        else:
            booking.seats, booking.total = old_seats, old_total
            print_error("Could not save changes. Your old seats are unchanged.")
    else:
        print_info("No changes were made.")


def cancel_booking(booking: Booking, bookings: list[Booking], found: list[Booking]) -> None:
    if show_has_started(booking):
        print_error("This show already started. It cannot be cancelled.")
        return
    if not ask_yes_no(f"Are you sure you want to cancel booking {booking.invoice}?"):
        print_info("The booking was not cancelled.")
        return
    remaining = [item for item in bookings if item is not booking]
    if save_bookings(remaining):
        bookings.remove(booking)
        found.remove(booking)
        print_success(f"Booking cancelled. Refund amount: {booking.total:.0f} SAR (simulation only).")
    else:
        print_error("Could not save cancellation. Your booking is unchanged.")


def my_bookings_menu() -> None:
    clear_screen()
    print_title("My Bookings")
    bookings = load_bookings()
    found = search_bookings(bookings)
    if not found:
        print_error("No bookings found. Check the name or invoice number.")
        input("\nPress Enter to return to the main menu...")
        return

    while found:
        clear_screen()
        print_title(f"Bookings of {found[0].customer}")
        found.sort(key=lambda booking: (booking.show_date, booking.show_time))  # nearest show first
        print_bookings_table(found)
        print()
        action = ask_menu(ACTIONS)
        if action == 5:
            return

        booking = pick_booking(found)
        print()
        if action == 1:
            booking.print_ticket()
        elif action == 2:
            change_seats(booking, bookings)
        elif action == 3:
            cancel_booking(booking, bookings, found)
        elif action == 4:
            path = export_ticket(booking)
            print_success(f"Ticket saved to {path}")
        input("\nPress Enter to continue...")

    print_info("You have no more bookings.")
    input("\nPress Enter to return to the main menu...")
