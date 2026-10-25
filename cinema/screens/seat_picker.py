"""Choosing seats from the seat map (used for new bookings and for changing seats)."""

from cinema.config.settings import MAX_SEATS_PER_BOOKING
from cinema.models.hall import Hall
from cinema.ui.display import print_error, print_info, print_success
from cinema.ui.inputs import ask_seat, ask_yes_no
from cinema.ui.seat_map import draw_seat_map


def calculate_total(hall: Hall, seats: list[str]) -> float:
    total = 0
    for seat in seats:
        total += hall.seat_price(seat)
    return total


def ask_free_seat(hall: Hall, taken: set[str], selected: list[str]) -> str:
    """Keep asking until the customer types a free seat (or Q)."""
    while True:
        seat = ask_seat()
        if seat == "Q":
            return seat
        if not seat:
            print_error("Please enter a seat number (example: B5), or Q to stop.")
        elif not hall.is_valid_seat(seat):
            print_error(f"'{seat}' is not a seat in this hall. Look at the map and try again.")
        elif seat in taken:
            print_error(f"Seat {seat} is already booked (red). Please choose a green seat.")
        elif seat in selected:
            print_error(f"You already chose {seat}.")
        else:
            return seat


def select_seats(hall: Hall, taken: set[str]) -> list[str]:
    """Let the customer pick one or more free seats. Returns the chosen seats."""
    selected = []
    while True:
        print()
        draw_seat_map(hall, taken, set(selected))
        if selected:
            print_info(f"Your seats: {', '.join(selected)}  |  Total: {calculate_total(hall, selected):.0f} SAR")

        seat = ask_free_seat(hall, taken, selected)
        if seat == "Q":
            return selected

        selected.append(seat)
        print_success(f"Seat {seat} ({hall.seat_type(seat)}, {hall.seat_price(seat):.0f} SAR) added.")

        if len(selected) >= MAX_SEATS_PER_BOOKING:
            print_info(f"Maximum {MAX_SEATS_PER_BOOKING} seats per booking.")
            return selected
        if len(selected) + len(taken) >= hall.capacity():
            print_info("No more free seats in this show.")
            return selected
        if not ask_yes_no("Do you want to book another seat (for a friend)?"):
            return selected
