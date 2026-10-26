from datetime import date, datetime, time, timedelta

import config
import storage
from models import Reservation


def parse_slot(date_str, time_str):
    try:
        return datetime.strptime(f"{date_str} {time_str}", config.DATETIME_FORMAT)
    except ValueError:
        raise ValueError("Wrong date/time. Use: YYYY-MM-DD HH:MM  (e.g. 2026-11-05 19:30)")


def validate_slot(dt):
    if dt < datetime.now():
        raise ValueError("That time is in the past.")
    end = dt + timedelta(minutes=config.BOOKING_DURATION_MINUTES)
    opening = dt.replace(hour=config.OPENING_HOUR, minute=0)
    closing = dt.replace(hour=config.CLOSING_HOUR, minute=0)
    if dt < opening or end > closing:
        raise ValueError(
            f"We are open {config.OPENING_HOUR}:00-{config.CLOSING_HOUR}:00 and each "
            f"booking lasts {config.BOOKING_DURATION_MINUTES} minutes."
        )


def validate_phone(phone):
    digits = phone.replace("+", "", 1)
    if not digits.isdigit() or not 9 <= len(digits) <= 15:
        raise ValueError("Phone must be 9-15 digits (e.g. 0501234567).")
    return phone


def validate_guests(guests):
    try:
        guests = int(guests)
    except (TypeError, ValueError):
        raise ValueError("Number of guests must be a whole number.")
    if guests < 1:
        raise ValueError("Number of guests must be at least 1.")
    return guests


def _overlaps(start_a, start_b):
    length = timedelta(minutes=config.BOOKING_DURATION_MINUTES)
    return start_a < start_b + length and start_b < start_a + length


def available_tables(dt, guests):
    """Free tables that fit `guests` at time `dt`, smallest table first."""
    busy = {
        r.table_id
        for r in storage.load_reservations()
        if r.status == "confirmed" and _overlaps(dt, r.start_dt)
    }
    fitting = [t for t in storage.load_tables()
               if t.capacity >= guests and t.id not in busy]
    return sorted(fitting, key=lambda t: t.capacity)


def occupied_now(now=None):
    """Ids of the tables that have a confirmed booking running right now."""
    now = now or datetime.now()
    return {r.table_id for r in storage.load_reservations()
            if r.status == "confirmed" and r.start_dt <= now < r.end_dt}


def create_reservation(name, phone, guests, dt, table_id=None):
    guests = validate_guests(guests)
    validate_slot(dt)
    options = available_tables(dt, guests)
    if not options:
        raise ValueError("Sorry, no table is available for that time and party size.")

    if table_id is None:
        chosen = options[0]  # smallest table that fits
    else:
        chosen = next((t for t in options if t.id == table_id), None)
        if chosen is None:
            raise ValueError("That table is not available.")

    reservations = storage.load_reservations()
    new_id = max((r.id for r in reservations), default=0) + 1
    reservation = Reservation(
        id=new_id,
        table_id=chosen.id,
        customer_name=name,
        phone=phone,
        guests=guests,
        start=dt.strftime(config.DATETIME_FORMAT),
    )
    reservations.append(reservation)
    storage.save_reservations(reservations)
    return reservation


def cancel_reservation(res_id, phone=None):
    """Cancel a booking. If `phone` is given, it must match the booking owner."""
    reservations = storage.load_reservations()
    target = next((r for r in reservations if r.id == res_id), None)
    if target is None:
        raise ValueError(f"No booking with id {res_id}.")
    if phone is not None and target.phone != phone:
        raise ValueError("That booking belongs to someone else.")
    if target.status == "cancelled":
        raise ValueError("That booking is already cancelled.")
    target.status = "cancelled"
    storage.save_reservations(reservations)
    return target


def get_reservation(res_id, phone=None):
    """Return one reservation. If `phone` is given, it must match the owner."""
    found = next((r for r in storage.load_reservations() if r.id == res_id), None)
    if found is None:
        raise ValueError(f"No booking with id {res_id}.")
    if phone is not None and found.phone != phone:
        raise ValueError("That booking belongs to someone else.")
    return found


def upcoming_reservations(phone=None):
    now = datetime.now()
    found = [r for r in storage.load_reservations()
             if r.status == "confirmed" and r.end_dt > now
             and (phone is None or r.phone == phone)]
    return sorted(found, key=lambda r: r.start_dt)


def reservations_on(date_str):
    try:
        day = datetime.strptime(date_str, config.DATE_FORMAT).date()
    except ValueError:
        raise ValueError("Wrong date. Use: YYYY-MM-DD")
    found = [r for r in storage.load_reservations()
             if r.status == "confirmed" and r.start_dt.date() == day]
    return sorted(found, key=lambda r: r.start_dt)


def stats():
    reservations = storage.load_reservations()
    confirmed = [r for r in reservations if r.status == "confirmed"]
    per_table = {}
    for r in confirmed:
        per_table[r.table_id] = per_table.get(r.table_id, 0) + 1
    busiest = max(per_table, key=per_table.get) if per_table else None
    return {
        "total": len(reservations),
        "confirmed": len(confirmed),
        "cancelled": len(reservations) - len(confirmed),
        "upcoming": len(upcoming_reservations()),
        "busiest_table": busiest,
    }


def next_days(count=None):
    """Today and the following days, as date objects."""
    count = count or config.BOOKING_WINDOW_DAYS
    return [date.today() + timedelta(days=i) for i in range(count)]


def time_slots(day):
    """All bookable start times on `day` (past times are skipped)."""
    slots = []
    current = datetime.combine(day, time(config.OPENING_HOUR, 0))
    last = (datetime.combine(day, time(config.CLOSING_HOUR, 0))
            - timedelta(minutes=config.BOOKING_DURATION_MINUTES))
    while current <= last:
        if current > datetime.now():
            slots.append(current)
        current += timedelta(minutes=config.SLOT_STEP_MINUTES)
    return slots


def _format_delta(delta):
    total_minutes = int(delta.total_seconds() // 60)
    days, rest = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(rest, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes or not parts:
        parts.append(f"{minutes}m")
    return " ".join(parts)


def time_status(reservation, now=None):
    """Tell how much time is left before/during a booking."""
    now = now or datetime.now()
    if reservation.status == "cancelled":
        return "cancelled"
    if now < reservation.start_dt:
        return f"starts in {_format_delta(reservation.start_dt - now)}"
    if now < reservation.end_dt:
        return f"{_format_delta(reservation.end_dt - now)} left"
    return "finished"