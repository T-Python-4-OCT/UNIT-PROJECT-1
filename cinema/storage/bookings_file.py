"""Read and write the bookings JSON file."""

import json
import os
import tempfile

from cinema.config.settings import BOOKINGS_FILE, DATA_DIR, TICKETS_DIR
from cinema.models.booking import Booking, booking_from_dict


def ensure_folders() -> None:
    """Create the data and tickets folders if they do not exist."""
    for folder in (DATA_DIR, TICKETS_DIR):
        if not os.path.exists(folder):
            os.makedirs(folder)


def load_bookings() -> list[Booking]:
    """Read stored bookings, refusing broken data instead of silently deleting it."""
    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
    except FileNotFoundError:
        return []
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read bookings file: {error}") from error

    if not isinstance(raw_data, list):
        raise ValueError("Bookings file should contain a list, not another JSON type.")
    bookings = []
    for item in raw_data:
        if not isinstance(item, dict):
            raise ValueError("Invalid booking entry in the bookings file.")
        try:
            booking = booking_from_dict(item)
            if (not isinstance(booking.invoice, int) or isinstance(booking.invoice, bool)
                    or not isinstance(booking.customer, str)
                    or not isinstance(booking.seats, list)
                    or not all(isinstance(seat, str) for seat in booking.seats)
                    or not isinstance(booking.total, (int, float))):
                raise ValueError("Invalid booking field types")
            bookings.append(booking)
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid booking entry: {error}") from error
    return bookings


def save_bookings(bookings: list[Booking]) -> bool:
    """Write a temporary file first, then atomically replace the old data file."""
    temp_path = None
    try:
        ensure_folders()
        data = [booking.to_dict() for booking in bookings]
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=DATA_DIR,
                                         suffix=".tmp", delete=False) as file:
            temp_path = file.name
            json.dump(data, file, indent=4, ensure_ascii=False)
        os.replace(temp_path, BOOKINGS_FILE)
        return True
    except (OSError, TypeError, ValueError):
        return False
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
