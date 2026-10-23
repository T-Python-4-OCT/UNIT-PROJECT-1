import uuid

from . import holds, storage
from .errors import NotFoundError
from .models import Cart, Match
from .pricing import TOTAL_SEATS


class Session:
    """Everything the current visitor needs: the data, the cart and the phone number."""

    def __init__(self) -> None:
        storage.ensure_data()
        self.cart = Cart()
        self.phone: str | None = None
        self.token = uuid.uuid4().hex          # tells my holds apart from other fans' holds
        self.reload()

    def reload(self) -> None:
        self.teams = storage.load_teams()
        self.matches = storage.load_matches()
        self.bookings = storage.load_bookings()

    def refresh_bookings(self) -> None:
        self.bookings = storage.load_bookings()

    def get_match(self, match_id: int) -> Match:
        for match in self.matches:
            if match.id == match_id:
                return match
        raise NotFoundError(f"No match with ID {match_id}.")

    def team_name(self, team_id: str) -> str:
        return self.teams[team_id].name_en

    def match_title(self, match: Match) -> str:
        return f"{self.team_name(match.home_id)} vs {self.team_name(match.away_id)}"

    def booked_seats(self, match_id: int) -> set[str]:
        seats = set()
        for b in self.bookings:
            if b.match_id == match_id and b.is_confirmed:
                seats.update(b.seats)
        return seats

    def free_seats(self, match: Match) -> int:
        return TOTAL_SEATS - len(self.booked_seats(match.id))

    def sorted_matches(self, matches: list[Match]) -> list[Match]:
        return sorted(matches, key=lambda m: (m.date, m.time, m.id))

    def sync_cart(self) -> list[str]:
        """Drop cart seats whose temporary hold has expired. Returns the lost seats."""
        lost = []
        for match_id, seats in self.cart.items().items():
            mine, _ = holds.seats_for(match_id, self.token)
            for seat in seats:
                if seat not in mine:
                    self.cart.remove(match_id, seat)
                    lost.append(seat)
        return lost

    def empty_cart(self) -> None:
        for match_id, seats in self.cart.items().items():
            for seat in seats:
                holds.release(match_id, seat, self.token)
        self.cart.clear()