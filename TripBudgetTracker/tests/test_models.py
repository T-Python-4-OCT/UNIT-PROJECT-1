"""Automatic tests for the money maths. Run them with:  pytest"""
from datetime import date

import pytest

from tripbudget.models import BudgetError, Expense, Ticket, Trip, ValidationError


def make_trip() -> Trip:
    """Istanbul, 9 days, 8000 SAR, 1 SAR = 9 TRY, ticket 1800."""
    trip = Trip("Istanbul", date(2026, 10, 20), date(2026, 10, 28), 8000, "SAR", "TRY", 9)
    trip.set_ticket(Ticket("TK1234", 1800))
    return trip


def test_ticket_is_taken_first():
    assert make_trip().trip_budget == 6200


def test_default_split():
    trip = make_trip()
    assert trip.category_budget("hotel") == 2480    # 40%
    assert trip.category_budget("reserve") == 930   # 15%


def test_currency_conversion():
    assert make_trip().to_base(450) == 50           # 450 TRY / 9 = 50 SAR


def test_spending_and_remaining():
    trip = make_trip()
    trip.add_expense(Expense("hotel", 300, day=date(2026, 10, 21)))
    assert trip.category_status("hotel") == (2480, 300, 2180)
    assert trip.remaining_total == 5900


def test_daily_allowance():
    trip = make_trip()
    trip.add_expense(Expense("food", 300, day=date(2026, 10, 22)))
    # 7 days left from Oct 22 to Oct 28: 5900 / 7
    assert trip.daily_allowance(date(2026, 10, 22)) == round(5900 / 7, 2)


def test_ticket_more_than_budget_is_refused():
    trip = Trip("Rome", date(2026, 1, 1), date(2026, 1, 5), 1000)
    with pytest.raises(BudgetError):
        trip.set_ticket(Ticket("A1", 2000))


@pytest.mark.parametrize("bad", [0, -5, float("nan"), float("inf")])
def test_bad_amounts_are_refused(bad):
    with pytest.raises(ValidationError):
        Expense("food", bad)


def test_split_must_add_up_to_100():
    with pytest.raises(ValidationError):
        make_trip().set_split({"hotel": 50, "food": 50, "activities": 10, "reserve": 0})


def test_save_and_load_keeps_everything():
    trip = make_trip()
    trip.add_expense(Expense("food", 50, "kebab", date(2026, 10, 21), 450, "TRY", 9))
    copy = Trip.from_dict(trip.to_dict())
    assert copy.to_dict() == trip.to_dict()
