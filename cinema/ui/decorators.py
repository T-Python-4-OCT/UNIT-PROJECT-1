"""Decorators used on the screens."""


def pause_after(func):
    """After the screen finishes, wait for Enter before going back to the menu."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        input("\nPress Enter to return to the main menu...")
        return result
    return wrapper
