from utils.errors import UsageError


def need(args, minimum, maximum=None):
    """Raise UsageError unless minimum <= len(args) <= maximum."""
    maximum = minimum if maximum is None else maximum
    if not minimum <= len(args) <= maximum:
        raise UsageError()


def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() in ("y", "yes")