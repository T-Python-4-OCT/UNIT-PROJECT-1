"""The 3 hall types. Each one inherits from Hall and changes only what is different."""

from cinema.models.hall import Hall


class StandardHall(Hall):
    """6 rows x 8 seats. Rows A-D regular (40 SAR), rows E-F premium (60 SAR)."""

    def __init__(self):
        super().__init__("Standard", rows=6, cols=8, price=40,
                         description="Classic cinema experience")
        self.premium_rows = ("E", "F")
        self.premium_price = 60

    def seat_price(self, seat: str) -> float:
        if seat[0] in self.premium_rows:
            return self.premium_price
        return self.price

    def seat_type(self, seat: str) -> str:
        if seat[0] in self.premium_rows:
            return "Premium"
        return "Regular"

    def row_divider(self, row: str) -> str:
        if row == self.premium_rows[0]:
            return "- - - - PREMIUM SEATS - - - -"
        return ""

    def price_info(self) -> str:
        return f"Rows A-D Regular: {self.price:.0f} SAR | Rows E-F Premium: {self.premium_price:.0f} SAR"


class ImaxHall(Hall):
    """6 rows x 10 seats, all seats 80 SAR, aisle in the middle."""

    def __init__(self):
        super().__init__("IMAX", rows=6, cols=10, price=80,
                         description="Giant screen and powerful sound")

    def has_aisle_after(self, col: int) -> bool:
        return col == 5


class SuitesHall(Hall):
    """4 rows x 8 seats in couple pairs (2 seats then a space), 150 SAR."""

    def __init__(self):
        super().__init__("Suites", rows=4, cols=8, price=150,
                         description="Luxury recliner seats in couple pairs")

    def has_aisle_after(self, col: int) -> bool:
        return col % 2 == 0


def get_halls() -> list[Hall]:
    """All hall types, in the order shown in the menu."""
    return [StandardHall(), ImaxHall(), SuitesHall()]


def get_hall_by_name(name: str) -> Hall | None:
    for hall in get_halls():
        if hall.name == name:
            return hall
    return None
