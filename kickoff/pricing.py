ROWS: str = "ABCDEF"
COLS: int = 10
MAX_SEATS_PER_MATCH: int = 5

NORTH_ROWS: str = "ABC"
SOUTH_ROWS: str = "DEF"
ROW_CATEGORY: dict[str, str] = {"A": "Family", "B": "Standard", "C": "VIP", "D": "VIP", "E": "Standard", "F": "Family"}
PRICES: dict[str, int] = {"VIP": 250, "Standard": 60, "Family": 30}
COUPONS: dict[str, int] = {"KICKOFF10": 10, "WELCOME5": 5}

TOTAL_SEATS: int = len(ROWS) * COLS


def seat_category(seat: str) -> str:
    return ROW_CATEGORY[seat[0]]


def seat_price(seat: str) -> int:
    return PRICES[seat_category(seat)]