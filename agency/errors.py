"""Custom exception for user-facing errors."""
class ServiceError(Exception):
    """An expected, user-facing problem (bad input, not found, rule broken).

    The UI layer catches this and shows the message in red.
    """
