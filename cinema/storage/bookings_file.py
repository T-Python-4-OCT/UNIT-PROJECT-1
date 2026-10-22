"""Read and write the bookings JSON file."""

import json
import os

from cinema.config.settings import BOOKINGS_FILE, DATA_DIR, TICKETS_DIR
from cinema.models.booking import Booking, booking_from_dict


def ensure_folders() -> None:
    """Create the data and tickets folders if they do not exist."""
    for folder in (DATA_DIR, TICKETS_DIR):
        if not os.path.exists(folder):
            os.makedirs(folder)


def load_bookings() -> list[Booking]:
    if not os.path.exists(BOOKINGS_FILE):
        return []  # first run: no bookings yet
    with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
        raw_data = json.load(file)
    bookings = []
    for item in raw_data:
        bookings.append(booking_from_dict(item))
    return bookings


def save_bookings(bookings: list[Booking]) -> bool:
    """Save all bookings. Returns True if it worked."""
    ensure_folders()
    data = [booking.to_dict() for booking in bookings]
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return True
