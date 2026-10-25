import config
from cli import ui
from services import booking


def print_tables(tables, title="Tables"):
    busy = booking.occupied_now()
    rows = []
    for t in tables:
        status = ui.red("Occupied now") if t.id in busy else ui.green("Free now")
        rows.append([t.id, t.capacity, t.location, status])
    ui.table(["ID", "Seats", "Location", "Status"], rows, title)


def colored_time(reservation):
    text = booking.time_status(reservation)
    if reservation.status == "cancelled" or text == "finished":
        return ui.red(text)
    if text.endswith("left"):
        return ui.yellow(text)
    return ui.green(text)


def print_reservations(reservations, show_customer=False, title="Bookings"):
    headers = ["ID", "When", "Guests", "Table", "Time"]
    if show_customer:
        headers += ["Customer", "Phone"]
    rows = []
    for r in reservations:
        row = [r.id, r.start, r.guests, r.table_id, colored_time(r)]
        if show_customer:
            row += [ui.esc(r.customer_name), ui.esc(r.phone)]
        rows.append(row)
    ui.table(headers, rows, title)


def print_receipt(reservation, table):
    seats = f"{table.capacity} seats, {table.location}" if table else "unknown"
    status = (ui.green(reservation.status) if reservation.status == "confirmed"
              else ui.red(reservation.status))
    ui.box([
        f"Reservation # : {reservation.id}",
        f"Name          : {ui.esc(reservation.customer_name)}",
        f"Phone         : {ui.esc(reservation.phone)}",
        f"Date & Time   : {reservation.start}",
        f"Duration      : {config.BOOKING_DURATION_MINUTES} minutes",
        f"Guests        : {reservation.guests}",
        f"Table         : {reservation.table_id} ({seats})",
        f"Status        : {status}",
        "",
        "Thank you for choosing us!",
    ], f"{config.RESTAURANT_NAME} - Booking Receipt", min_width=42)


def choose_date(title="Choose a date"):
    days = booking.next_days()
    labels = []
    for i, day in enumerate(days):
        tag = " (today)" if i == 0 else " (tomorrow)" if i == 1 else ""
        labels.append(f"{day:%a %d %b %Y}{tag}")
    index = ui.menu(title, labels, "Cancel")
    return None if index is None else days[index]


def pick_booking(reservations, title, show_customer=False, empty_text="No upcoming bookings."):
    if not reservations:
        ui.box([ui.red(empty_text)])
        return None
    labels = []
    for r in reservations:
        label = f"#{r.id}  {r.start}  {r.guests} guests  table {r.table_id}"
        if show_customer:
            label += f"  {ui.esc(r.customer_name)}"
        labels.append(label)
    index = ui.menu(title, labels, "Back")
    return None if index is None else reservations[index]
