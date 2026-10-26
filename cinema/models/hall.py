"""The base Hall class: seats, prices and booked seats of one hall."""

import random

ROW_LETTERS = "ABCDEFGHIJ"
TAKEN_RATIO = 0.3  # around 30% of seats are already booked by other people


class Hall:
    """Base class for every hall type (Standard, IMAX, Suites)."""

    def __init__(self, name: str, rows: int, cols: int, price: float, description: str):
        self.name = name
        self.rows = rows
        self.cols = cols
        self.price = price
        self.description = description

    def row_labels(self) -> list[str]:
        return list(ROW_LETTERS[: self.rows])

    def all_seats(self) -> list[str]:
        seats = []
        for row in self.row_labels():
            for col in range(1, self.cols + 1):
                seats.append(f"{row}{col}")
        return seats

    def capacity(self) -> int:
        return self.rows * self.cols

    def is_valid_seat(self, seat: str) -> bool:
        return seat in self.all_seats()

    def seat_price(self, seat: str) -> float:
        return self.price

    def seat_type(self, seat: str) -> str:
        return self.name

    def price_info(self) -> str:
        return f"All seats: {self.price:.0f} SAR"

    def has_aisle_after(self, col: int) -> bool:
        """Child classes return True where they want an empty space."""
        return False

    def row_divider(self, row: str) -> str:
        """Text printed above a row (used to mark premium rows)."""
        return ""

    def taken_by_others(self, show_key: str) -> set[str]:
        """Seats booked by other customers.

        The same show_key always gives the same seats, so the map
        looks the same every time you open the same show.
        """
        generator = random.Random(show_key)
        count = int(self.capacity() * TAKEN_RATIO)
        return set(generator.sample(self.all_seats(), count))
