"""'My bookings': find bookings by name or invoice, then view, change seats or export."""

from cinema.models.booking import Booking
from cinema.models.hall_types import get_hall_by_name
from cinema.screens.seat_picker import calculate_total, select_seats
from cinema.storage.bookings_file import load_bookings, save_bookings
from cinema.storage.search import booked_seats, find_by_invoice, find_by_name
from cinema.storage.tickets import export_ticket
from cinema.ui.display import clear_screen, print_error, print_info, print_success, print_title
from cinema.ui.inputs import ask_menu, ask_number, ask_yes_no

ACTIONS = ["View ticket", "Change seats", "Save ticket as text file", "Back to main menu"]


def search_bookings(bookings: list[Booking]) -> list[Booking]:
    query = input("Enter your full name or invoice number: ").strip()
    if query.isdigit():
        booking = find_by_invoice(bookings, int(query))
        if booking is None:
            return []
        return [booking]
    return find_by_name(bookings, query)


def print_bookings_table(found: list[Booking]) -> None:
    """Every booking as a small card."""
    for number, booking in enumerate(found, start=1):
        print(f"[{number}] Invoice {booking.invoice}  |  {booking.movie}")
        print(f"    Cinema        : {booking.branch}")
        print(f"    Experience    : {booking.hall}")
        print(f"    Your showtime : {booking.show_date_text()} at {booking.show_time}")
        print(f"    Seats         : {booking.seats_text()}   |   Total: {booking.total:.0f} SAR")
        print("-" * 60)


def pick_booking(found: list[Booking]) -> Booking:
    if len(found) == 1:
        return found[0]
    number = ask_number("Which booking? (number in [ ]): ", 1, len(found))
    return found[number - 1]


def print_price_difference(old_total: float, new_total: float) -> None:
    difference = new_total - old_total
    if difference > 0:
        print_info(f"You will pay {difference:.0f} SAR more.")
    elif difference < 0:
        print_info(f"You will get {abs(difference):.0f} SAR back.")


def change_seats(booking: Booking, bookings: list[Booking]) -> None:
    hall = get_hall_by_name(booking.hall)
    if hall is None:
        print_error("Unknown hall in this booking.")
        return

    # Your old seats are free again, so they show green on the map
    taken = hall.taken_by_others(booking.show_key()) | booked_seats(bookings, booking.show_key(), booking.invoice)
    print_info(f"Your current seats: {booking.seats_text()} ({booking.total:.0f} SAR). Choose your new seats:")
    new_seats = select_seats(hall, taken)
    if not new_seats:
        print_info("No seats were chosen. Your booking stays the same.")
        return

    new_total = calculate_total(hall, new_seats)
    print()
    print(f"Old seats: {booking.seats_text():<20} {booking.total:.0f} SAR")
    print(f"New seats: {', '.join(new_seats):<20} {new_total:.0f} SAR")
    print_price_difference(booking.total, new_total)

    if ask_yes_no("Save the new seats?"):
        booking.seats = new_seats
        booking.total = new_total
        save_bookings(bookings)
        print_success("Seats updated.")
    else:
        print_info("No changes were made.")


def my_bookings_menu() -> None:
    clear_screen()
    print_title("My Bookings")
    bookings = load_bookings()
    found = search_bookings(bookings)
    if not found:
        print_error("No bookings found. Check the name or invoice number.")
        input("\nPress Enter to return to the main menu...")
        return

    while True:
        clear_screen()
        print_title(f"Bookings of {found[0].customer}")
        found.sort(key=lambda booking: (booking.show_date, booking.show_time))  # nearest show first
        print_bookings_table(found)
        print()
        action = ask_menu(ACTIONS)
        if action == 4:
            return

        booking = pick_booking(found)
        print()
        if action == 1:
            booking.print_ticket()
        elif action == 2:
            change_seats(booking, bookings)
        elif action == 3:
            path = export_ticket(booking)
            print_success(f"Ticket saved to {path}")
        input("\nPress Enter to continue...")
