"""Save a ticket as a text file inside the tickets folder."""

import os

from cinema.config.settings import TICKETS_DIR
from cinema.models.booking import Booking
from cinema.storage.bookings_file import ensure_folders


def export_ticket(booking: Booking) -> str:
    """Write the ticket to tickets/ticket_<invoice>.txt and return the file path."""
    ensure_folders()
    path = os.path.join(TICKETS_DIR, f"ticket_{booking.invoice}.txt")
    with open(path, "w", encoding="utf-8") as file:
        file.write(booking.ticket_text())
    return path
