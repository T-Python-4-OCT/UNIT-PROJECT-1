"""Custom exceptions used across the app (Lesson 8: exception handling)."""


class TripError(Exception):
    """Base class for every error this app raises on purpose."""


class ValidationError(TripError):
    """The user gave a value that doesn't make sense (negative amount, bad date...)."""


class BudgetError(TripError):
    """An operation would break the budget rules (e.g. ticket costs more than the budget)."""


class StorageError(TripError):
    """Reading or writing the data file failed."""
