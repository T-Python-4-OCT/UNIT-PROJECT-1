"""Data models and errors (Lesson 6: data structures, Lesson 8: exceptions, Lesson 9: OOP).

Item     -> base class (a money amount that must be > 0)
Ticket   -> Item + ticket number
Expense  -> Item + category, note, date (+ the original foreign amount)
Trip     -> the budget, the ticket, the split and all expenses
"""
from __future__ import annotations

import math
from datetime import date, timedelta


# ---------- errors ----------
class TripError(Exception):
    """Base class for every error this app raises on purpose."""


class ValidationError(TripError):
    """A value that doesn't make sense (negative amount, bad date...)."""


class BudgetError(TripError):
    """Something that breaks the budget rules (ticket costs more than the budget)."""


class StorageError(TripError):
    """Reading or writing the data file failed."""


# Tuple: the categories never change.
CATEGORIES: tuple[str, ...] = ("hotel", "food", "activities", "reserve")

# Dictionary: category -> percentage of the trip budget.
DEFAULT_SPLIT: dict[str, int] = {"hotel": 40, "food": 25, "activities": 20, "reserve": 15}


# ---------- classes ----------
class Item:
    """Base class: anything that has a money amount."""

    def __init__(self, amount: float) -> None:
        if not math.isfinite(amount) or amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        self._amount = round(float(amount), 2)

    @property
    def amount(self) -> float:  # read-only from outside (encapsulation)
        return self._amount


class Ticket(Item):
    def __init__(self, number: str, price: float) -> None:
        super().__init__(price)
        self.number = number.strip().upper()

    def to_dict(self) -> dict:
        return {"number": self.number, "price": self.amount}


class Expense(Item):
    def __init__(self, category: str, amount: float, note: str = "",
                 day: date | None = None, local_amount: float | None = None,
                 local_currency: str | None = None, rate: float | None = None) -> None:
        """`amount` is always in the budget currency (e.g. SAR).
        If you paid in another currency, the original amount and rate are kept,
        so old expenses never change when the rate changes."""
        super().__init__(amount)
        if category not in CATEGORIES:
            raise ValidationError(f"Unknown category: {category}")
        self.category = category
        self.note = note.strip()
        self.day = day or date.today()
        self.local_amount = local_amount
        self.local_currency = local_currency
        self.rate = rate

    def to_dict(self) -> dict:
        return {"category": self.category, "amount": self.amount, "note": self.note,
                "day": self.day.isoformat(), "local_amount": self.local_amount,
                "local_currency": self.local_currency, "rate": self.rate}

    @classmethod
    def from_dict(cls, data: dict) -> Expense:
        return cls(data["category"], data["amount"], data["note"],
                   date.fromisoformat(data["day"]), data.get("local_amount"),
                   data.get("local_currency"), data.get("rate"))


class Trip:
    def __init__(self, destination: str, start: date, end: date, total_budget: float,
                 currency: str = "SAR", local_currency: str | None = None,
                 rate: float = 1.0) -> None:
        if not destination.strip():
            raise ValidationError("Destination can't be empty.")
        if end < start:
            raise ValidationError("End date can't be before the start date.")
        if not math.isfinite(total_budget) or total_budget <= 0:
            raise ValidationError("Budget must be greater than zero.")
        if not math.isfinite(rate) or rate <= 0:
            raise ValidationError("Exchange rate must be greater than zero.")

        self.destination = destination.strip()
        self.start = start
        self.end = end
        self.total_budget = round(float(total_budget), 2)
        self.currency = currency.upper()                          # e.g. SAR
        self.local_currency = (local_currency or currency).upper()  # e.g. TRY
        self.rate = float(rate)                                    # 1 SAR = rate TRY
        self.ticket: Ticket | None = None
        self.split: dict[str, int] = dict(DEFAULT_SPLIT)
        self.expenses: list[Expense] = []

    # ---------- budget ----------
    def set_ticket(self, ticket: Ticket) -> None:
        if ticket.amount > self.total_budget:
            raise BudgetError("The ticket costs more than your whole budget.")
        self.ticket = ticket

    @property
    def trip_budget(self) -> float:
        """What is left for the trip after paying for the ticket."""
        ticket_cost = self.ticket.amount if self.ticket else 0
        return round(self.total_budget - ticket_cost, 2)

    def set_split(self, split: dict[str, int]) -> None:
        if sum(split.values()) != 100:
            raise ValidationError(f"Percentages must add up to 100 (you gave {sum(split.values())}).")
        self.split = dict(split)

    def category_budget(self, category: str) -> float:
        return round(self.trip_budget * self.split[category] / 100, 2)

    # ---------- currency ----------
    def uses_foreign_currency(self) -> bool:
        return self.local_currency != self.currency

    def to_base(self, local_amount: float) -> float:
        """TRY -> SAR. With rate 9: 450 TRY = 50 SAR."""
        return round(local_amount / self.rate, 2)

    # ---------- spending ----------
    def add_expense(self, expense: Expense) -> None:
        self.expenses.append(expense)

    def remove_expense(self, index: int) -> Expense:
        if not 0 <= index < len(self.expenses):
            raise ValidationError("No expense with that number.")
        return self.expenses.pop(index)

    def spent_in(self, category: str) -> float:
        return round(sum(e.amount for e in self.expenses if e.category == category), 2)

    def category_status(self, category: str) -> tuple[float, float, float]:
        """Return (budget, spent, remaining) for one category."""
        budget = self.category_budget(category)
        spent = self.spent_in(category)
        return budget, spent, round(budget - spent, 2)

    @property
    def total_spent(self) -> float:
        return round(sum(e.amount for e in self.expenses), 2)

    @property
    def remaining_total(self) -> float:
        return round(self.trip_budget - self.total_spent, 2)

    def days_with_spending(self) -> set[date]:
        return {e.day for e in self.expenses}

    # ---------- time ----------
    def days_total(self) -> int:
        return (self.end - self.start).days + 1

    def days_elapsed(self, today: date) -> int:
        """Trip days that have passed (0 before the trip starts)."""
        return max(0, min((today - self.start).days + 1, self.days_total()))

    def days_left(self, today: date) -> int:
        """Trip days still ahead, counting today."""
        if today > self.end:
            return 0
        return (self.end - max(today, self.start)).days + 1

    def daily_allowance(self, today: date) -> float:
        days = self.days_left(today)
        return round(self.remaining_total / days, 2) if days else 0.0

    def is_finished(self, today: date) -> bool:
        return today > self.end

    def extend(self, extra_days: int) -> None:
        if extra_days < 1:
            raise ValidationError("You must add at least 1 day.")
        self.end += timedelta(days=extra_days)

    # ---------- saving ----------
    def to_dict(self) -> dict:
        return {
            "destination": self.destination, "start": self.start.isoformat(),
            "end": self.end.isoformat(), "total_budget": self.total_budget,
            "currency": self.currency, "local_currency": self.local_currency,
            "rate": self.rate, "ticket": self.ticket.to_dict() if self.ticket else None,
            "split": self.split, "expenses": [e.to_dict() for e in self.expenses],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Trip:
        trip = cls(data["destination"], date.fromisoformat(data["start"]),
                   date.fromisoformat(data["end"]), data["total_budget"],
                   data["currency"], data.get("local_currency"), data.get("rate", 1.0))
        if data.get("ticket"):
            trip.ticket = Ticket(data["ticket"]["number"], data["ticket"]["price"])
        trip.split = dict(data["split"])
        trip.expenses = [Expense.from_dict(e) for e in data["expenses"]]
        return trip
