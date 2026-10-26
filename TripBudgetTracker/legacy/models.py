from __future__ import annotations

import math
from datetime import date, timedelta
from unicodedata import category


class TripError(Exception):
    pass

class ValidationError(TripError):
    pass

class BudgetError(TripError):
    pass

class StorageError(TripError):
    pass




CATEGORIES: tuple[str, ...] = (
    "hotel",
    "food",
    "activities",
    "reserve",
)

DEFAULT_SPLIT: dict[str, int] = {
    "hotel": 40,
    "food": 25,
    "activities": 20,
    "reserve": 15,
}




class Item:
    """Base class: anything that has a money amount."""

    def __init__(self, amount: float) -> None:
        if not math.isfinite(amount) or amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        self._amount = round(float(amount), 2)

    @property
    def amount(self) -> float:
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
