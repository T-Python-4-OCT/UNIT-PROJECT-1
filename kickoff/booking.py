from datetime import datetime

from . import holds, storage
from .errors import (EmptyCartError, InvalidSeatError, KickoffError, MatchClosedError, NotFoundError,
                     SeatHeldError, SeatTakenError)
from .models import Booking
from .pricing import COLS, COUPONS, ROWS, seat_category, seat_price


def normalize_seat(code: str) -> str:
    seat = code.strip().upper()
    if len(seat) >= 2 and seat[0] in ROWS and seat[1:].isdigit() and 1 <= int(seat[1:]) <= COLS:
        return seat
    raise InvalidSeatError(f"'{code}' is not a seat. Use a row {ROWS[0]}-{ROWS[-1]} and number 1-{COLS}, like A3.")


def toggle_seat(session, match, code: str) -> tuple[str, bool]:
    """Add the seat to the cart, or remove it if it is already there. Returns (seat, added)."""
    if not match.is_open:
        raise MatchClosedError("This match is not open for booking.")
    seat = normalize_seat(code)
    if seat in session.booked_seats(match.id):
        raise SeatTakenError(f"{seat} is already booked.")
    if seat in session.cart.seats(match.id):          # second time = remove it
        session.cart.remove(match.id, seat)
        holds.release(match.id, seat, session.token)
        return seat, False
    session.cart.add(match.id, seat)               # may raise CartLimitError
    try:
        holds.hold(match.id, seat, session.token)     # may raise SeatHeldError
    except KickoffError:
        session.cart.remove(match.id, seat)
        raise
    return seat, True


def cart_lines(session):
    lines = []
    for match_id, seats in session.cart.items().items():
        match = session.get_match(match_id)
        for seat in seats:
            lines.append((match, seat, seat_price(seat)))
    return lines


def cart_subtotal(session):
    return sum(price for _, _, price in cart_lines(session))


def discount_percent(code: str) -> int:
    percent = COUPONS.get(code.strip().upper())
    if percent is None:
        raise KickoffError("This coupon code is not valid.")
    return percent


def checkout(session, name, phone, payment, percent=0):
    if session.cart.is_empty():
        raise EmptyCartError("Your cart is empty.")
    session.refresh_bookings()
    lost = session.sync_cart()
    if lost:
        raise SeatHeldError(f"Your hold expired for: {', '.join(lost)}. Please choose the seats again.")
    if session.cart.is_empty():
        raise EmptyCartError("Your cart is empty.")
    for match_id, seats in session.cart.items().items():
        match = session.get_match(match_id)
        if not match.is_open:
            raise MatchClosedError(f"{session.match_title(match)} is no longer open for booking.")
        taken = set(seats) & session.booked_seats(match_id)
        if taken:
            for seat in taken:
                session.cart.remove(match_id, seat)      # they are not ours anymore
            raise SeatTakenError(f"Someone just booked: {', '.join(sorted(taken))}. Please choose other seats.")
    subtotal = cart_subtotal(session)
    final_total = round(subtotal * (1 - percent / 100), 2)
    reference = payment.pay(final_total)
    created = []
    for match_id, seats in session.cart.items().items():
        part = sum(seat_price(s) for s in seats)
        booking = Booking(storage.next_booking_id(session.bookings), match_id, list(seats), name, phone, reference,
                          round(part * (1 - percent / 100), 2), percent, "confirmed",
                          datetime.now().strftime("%Y-%m-%d %H:%M"))
        session.bookings.append(booking)
        created.append(booking)
    storage.save_bookings(session.bookings)
    for booking in created:
        storage.save_ticket_file(booking.id, receipt_text(session, booking))
    session.empty_cart()
    session.phone = phone
    return created


def receipt_text(session, booking):
    match = session.get_match(booking.match_id)
    home = session.teams[match.home_id].name_en
    away = session.teams[match.away_id].name_en
    seats = ", ".join(f"{s} ({seat_category(s)})" for s in booking.seats)
    lines = [
        "KICKOFF TICKETS - E-TICKET",
        "-" * 40,
        f"Booking ID : {booking.id}",
        f"Match      : {home} vs {away}",
        f"Date / Time: {match.date} {match.time}",
        f"Stadium    : {match.stadium}, {match.city}",
        f"Seats      : {seats}",
        f"Paid       : {booking.total:.2f} SAR ({booking.payment})",
        f"Discount   : {booking.discount}%",
        f"Name       : {booking.name}",
        f"Status     : {booking.status.upper()}",
    ]
    return "\n".join(lines) + "\n"


def bookings_of(session, phone):
    session.refresh_bookings()
    return [b for b in session.bookings if b.phone == phone]


def cancel_booking(session, booking_id, phone):
    session.refresh_bookings()
    for booking in session.bookings:
        if booking.id.upper() == booking_id.upper() and booking.phone == phone:
            if not booking.is_confirmed:
                raise KickoffError("This booking is not active.")
            if not session.get_match(booking.match_id).is_open:
                raise MatchClosedError("You cannot cancel a booking for a match that is not upcoming.")
            booking.status = "cancelled"
            storage.save_bookings(session.bookings)
            return booking
    raise NotFoundError("No booking found with this ID for your phone number.")