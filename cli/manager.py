from getpass import getpass

import config
from cli import ui
from cli.common import (choose_date, pick_booking, print_reservations,
                        print_tables)
from services import auth, booking, tables
import storage

OPTIONS = [
    "View tables",
    "Add a table",
    "Remove a table",
    "Upcoming bookings",
    "Bookings by date",
    "Cancel a booking",
    "Statistics",
]


def _create_password():
    """First time only: the manager chooses a password. Returns True if it was saved."""
    ui.box(["No manager password yet.",
            f"Create one now (at least {config.MIN_PASSWORD_LENGTH} characters)."],
           "First-time setup")
    while True:
        first = getpass("New password (empty = cancel): ")
        if not first:
            print("Cancelled.")
            return False
        if getpass("Repeat the password: ") != first:
            ui.error("The two passwords do not match. Try again.")
            continue
        try:
            auth.set_password(first)   # also checks the minimum length
        except ValueError as err:
            ui.error(str(err))
            continue
        ui.success("Password saved. It is stored hashed, not as plain text.")
        return True


def _login():
    if not auth.password_is_set():
        return _create_password()

    for attempt in range(config.MAX_LOGIN_ATTEMPTS):
        if auth.verify_password(getpass("Manager password: ")):
            return True
        left = config.MAX_LOGIN_ATTEMPTS - attempt - 1
        ui.error(f"Wrong password. ({left} attempts left)")
    ui.error("Too many wrong attempts.")
    return False


def _add_table():
    seats = ui.ask_int("Number of seats (1-20): ", 1, 20)
    index = ui.menu("Table location", [l.title() for l in config.LOCATIONS], "Cancel")
    if index is None:
        return
    t = tables.add_table(seats, config.LOCATIONS[index])
    ui.success(f"Added table {t.id} ({t.capacity} seats, {t.location}).")


def _remove_table():
    all_tables = storage.load_tables()
    labels = [f"Table {t.id} - {t.capacity} seats, {t.location}" for t in all_tables]
    index = ui.menu("Remove which table?", labels, "Cancel")
    if index is None:
        return
    chosen = all_tables[index]
    if ui.confirm(f"Remove table {chosen.id}?"):
        tables.remove_table(chosen.id)
        ui.success("Table removed.")


def _stats():
    s = booking.stats()
    ui.box([
        f"Total bookings : {s['total']}",
        f"Confirmed      : {s['confirmed']}",
        f"Cancelled      : {s['cancelled']}",
        f"Upcoming       : {s['upcoming']}",
        f"Busiest table  : {s['busiest_table'] or '-'}",
    ], "Statistics")


def run_manager():
    if not _login():
        return

    while True:
        choice = ui.menu("Manager Menu", OPTIONS, "Logout")
        try:
            if choice is None:
                return
            elif choice == 0:
                print_tables(storage.load_tables())
            elif choice == 1:
                _add_table()
            elif choice == 2:
                _remove_table()
            elif choice == 3:
                print_reservations(booking.upcoming_reservations(), True, "Upcoming bookings")
            elif choice == 4:
                day = choose_date("Bookings on which day?")
                if day:
                    found = booking.reservations_on(day.strftime(config.DATE_FORMAT))
                    print_reservations(found, True, f"Bookings on {day:%a %d %b %Y}")
            elif choice == 5:
                r = pick_booking(booking.upcoming_reservations(), "Cancel which booking?", True)
                if r and ui.confirm(f"Cancel booking #{r.id} ({ui.esc(r.customer_name)})?"):
                    booking.cancel_reservation(r.id)
                    ui.success("Booking cancelled.")
            elif choice == 6:
                _stats()
        except ValueError as err:
            ui.error(f"Error: {err}")