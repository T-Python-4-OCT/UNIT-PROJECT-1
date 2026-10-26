from .errors import CartLimitError
from .pricing import MAX_SEATS_PER_MATCH


class Team:
    def __init__(self, team_id: str, name_en: str, city: str, logo: str,
                 played: int, won: int, drawn: int, lost: int, gf: int, ga: int) -> None:
        self.team_id = team_id
        self.name_en = name_en
        self.city = city
        self.logo = logo
        self.played = played
        self.won = won
        self.drawn = drawn
        self.lost = lost
        self.gf = gf          # goals for
        self.ga = ga          # goals against

    @property
    def points(self) -> int:
        return self.won * 3 + self.drawn

    @property
    def goal_diff(self) -> int:
        return self.gf - self.ga

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        return cls(**data)


class Match:
    def __init__(self, id: int, home_id: str, away_id: str, date: str, time: str, stadium: str, city: str,
                 status: str, home_goals: int | None = None, away_goals: int | None = None) -> None:
        self.id = id
        self.home_id = home_id
        self.away_id = away_id
        self.date = date
        self.time = time
        self.stadium = stadium
        self.city = city
        self.status = status              # "upcoming" or "finished"
        self.home_goals = home_goals
        self.away_goals = away_goals

    @property
    def is_open(self) -> bool:
        return self.status == "upcoming"

    def involves(self, team_id: str) -> bool:
        return team_id in (self.home_id, self.away_id)

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        return cls(**data)


class Booking:
    def __init__(self, id: str, match_id: int, seats: list[str], name: str, phone: str, payment: str,
                 total: float, discount: int, status: str, created: str) -> None:
        self.id = id
        self.match_id = match_id
        self.seats = seats
        self.name = name
        self.phone = phone
        self.payment = payment
        self.total = total
        self.discount = discount
        self.status = status              # "confirmed" or "cancelled"
        self.created = created

    @property
    def is_confirmed(self) -> bool:
        return self.status == "confirmed"

    def to_dict(self) -> dict:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict) -> "Booking":
        return cls(**data)


class Cart:

    def __init__(self) -> None:
        self.__items: dict[int, set[str]] = {}

    def seats(self, match_id: int) -> set[str]:
        return set(self.__items.get(match_id, set()))

    def add(self, match_id: int, seat: str) -> None:
        chosen = self.__items.setdefault(match_id, set())
        if len(chosen) >= MAX_SEATS_PER_MATCH:
            raise CartLimitError(f"You can hold at most {MAX_SEATS_PER_MATCH} seats per match.")
        chosen.add(seat)

    def remove(self, match_id: int, seat: str) -> bool:
        chosen = self.__items.get(match_id, set())
        if seat not in chosen:
            return False
        chosen.remove(seat)
        if not chosen:
            del self.__items[match_id]
        return True

    def clear(self) -> None:
        self.__items.clear()

    def is_empty(self) -> bool:
        return not self.__items

    def items(self) -> dict[int, list[str]]:
        return {match_id: sorted(seats) for match_id, seats in self.__items.items()}