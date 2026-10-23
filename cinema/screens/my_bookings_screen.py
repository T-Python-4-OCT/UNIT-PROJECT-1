"""'My bookings': find bookings by name or invoice, then show them."""

from cinema.models.booking import Booking
from cinema.storage.bookings_file import load_bookings
from cinema.storage.search import find_by_invoice, find_by_name
from cinema.ui.display import clear_screen, print_error, print_title


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


def my_bookings_menu() -> None:
    clear_screen()
    print_title("My Bookings")
    bookings = load_bookings()
    found = search_bookings(bookings)
    if not found:
        print_error("No bookings found. Check the name or invoice number.")
        input("\nPress Enter to return to the main menu...")
        return

    clear_screen()
    print_title(f"Bookings of {found[0].customer}")
    found.sort(key=lambda booking: (booking.show_date, booking.show_time))  # nearest show first
    print_bookings_table(found)
    input("\nPress Enter to return to the main menu...")
