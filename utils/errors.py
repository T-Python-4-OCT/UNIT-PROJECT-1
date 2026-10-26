class ClinicError(Exception):
    """Expected, user-facing error (shown as a friendly message)."""


class UsageError(ClinicError):
    """Raised when a command is used with the wrong arguments."""
    