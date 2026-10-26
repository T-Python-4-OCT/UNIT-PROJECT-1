import config
from cli import ui
from cli.common import (choose_date, pick_booking, print_receipt,
                        print_reservations, print_tables)
import storage
from services import booking, tables

OPTIONS = [
    "Browse tables",
    "Search tables",
    "Book a table",
    "My bookings",
    "Get a receipt",
    "Cancel a booking",
]


def _ask_name(text):
    if not text:
        raise ValueError("Name cannot be empty.")
    return text


def _search():
    kind = ui.menu("Search tables", ["By location", "By minimum seats"], "Back")
    if kind is None:
        return
    if kind == 0:
        index = ui.menu("Choose a location", [l.title() for l in config.LOCATIONS], "Back")
        if index is None:
            return
        found = tables.search_tables(config.LOCATIONS[index])
    else:
        seats = ui.ask_int("Minimum seats (1-20): ", 1, 20)
        found = tables.search_tables(str(seats))
    print_tables(found, "Search results")


def _book(name, phone):
    guests = ui.ask_int("Number of guests (1-20): ", 1, 20)
    fitting = sorted((t for t in storage.load_tables() if t.capacity >= guests),
                     key=lambda t: t.capacity)
    if not fitting:
        ui.error("No table is big enough for that many guests.")
        return

    day = choose_date("Choose a date")
    if day is None:
        return
    slots = booking.time_slots(day)
    if not slots:
        ui.error("No more times are available on that day.")
        return

    free_per_slot = [booking.available_tables(slot, guests) for slot in slots]
    labels = [f"{slot:%H:%M}   ({len(free)} table(s) free)" if free
              else f"{slot:%H:%M}   (full)"
              for slot, free in zip(slots, free_per_slot)]
    index = ui.menu("Choose a time", labels, "Cancel", [bool(f) for f in free_per_slot])
    if index is None:
        return
    slot, free = slots[index], free_per_slot[index]

    free_ids = {t.id for t in free}
    labels = [f"Table {t.id} - {t.capacity} seats, {t.location}"
              + ("" if t.id in free_ids else "   (booked)") for t in fitting]
    index = ui.menu("Choose a table", labels, "Cancel", [t.id in free_ids for t in fitting])
    if index is None:
        return

    reservation = booking.create_reservation(name, phone, guests, slot, fitting[index].id)
    ui.success("\nBooked successfully!")
    print_receipt(reservation, tables.get_table(reservation.table_id))


def run_customer():
    name = ui.ask_valid("Your name: ", _ask_name)
    phone = ui.ask_valid("Your phone number (e.g. 0501234567): ", booking.validate_phone)
    ui.console.print(f"\nWelcome, {ui.esc(name)}!")

    while True:
        choice = ui.menu(f"Customer Menu - {ui.esc(name)}", OPTIONS, "Back to main menu")
        try:
            if choice is None:
                return
            elif choice == 0:
                print_tables(storage.load_tables())
            elif choice == 1:
                _search()
            elif choice == 2:
                _book(name, phone)
            elif choice == 3:
                print_reservations(booking.upcoming_reservations(phone), title="My bookings")
            elif choice == 4:
                r = pick_booking(booking.upcoming_reservations(phone), "Receipt for which booking?")
                if r:
                    print_receipt(r, tables.get_table(r.table_id))
            elif choice == 5:
                r = pick_booking(booking.upcoming_reservations(phone), "Cancel which booking?")
                if r and ui.confirm(f"Cancel booking #{r.id}?"):
                    booking.cancel_reservation(r.id, phone)
                    ui.success("Booking cancelled.")
        except ValueError as err:
            ui.error(f"Error: {err}")
