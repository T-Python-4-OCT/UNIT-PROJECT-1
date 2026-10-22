"""Search inside the bookings list."""

import random

from cinema.models.booking import Booking


def booked_seats(bookings: list[Booking], show_key: str, skip_invoice: int | None = None) -> set[str]:
    """All seats saved for one show. skip_invoice is used when editing a booking."""
    seats = set()
    for booking in bookings:
        if booking.show_key() == show_key and booking.invoice != skip_invoice:
            seats.update(booking.seats)
    return seats


def new_invoice_number(bookings: list[Booking]) -> int:
    """A random 5-digit number that is not used before."""
    used_numbers = {booking.invoice for booking in bookings}
    number = random.randint(10000, 99999)
    while number in used_numbers:
        number = random.randint(10000, 99999)
    return number
