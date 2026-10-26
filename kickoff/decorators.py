import functools

from . import storage, ui
from .errors import KickoffError


def log_action(label):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is not False:          
                storage.log(label)
            return result
        return wrapper
    return decorator


def safe_action(func):
    """Show our own errors as a clean red message instead of crashing the program."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KickoffError as problem:
            ui.error(str(problem))
    return wrapper