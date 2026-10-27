# Python Modules and Packages
from functools import wraps

import psutil


# Python OOP - Classes
class ToolError(RuntimeError):
    pass


# Python Functions, Arguments and Return Values
def format_bytes(size):
    # Python Data Structures - Tuple
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    # Python Flow Control - Loops
    for unit in units:
        # Python Flow Control - Conditionals
        if abs(size) < 1024 or unit == units[-1]:
            # Python String Operations
            return f"{size:,.1f} {unit}"
        # Python Arithmetic Operations
        size /= 1024


def confirm(message):
    while True:
        answer = input(f"{message} [yes/no]: ").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n", ""):
            return False
        print("Please enter yes or no.")


def read_number(message, minimum, maximum):
    while True:
        # Exception Handling in Python
        try:
            number = int(input(message))
            if minimum <= number <= maximum:
                return number
        except ValueError:
            pass
        print(f"Enter a whole number from {minimum} to {maximum}.")


# Python Decorators
def logged_action(function):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        self.store.log(function.__name__, "started")
        try:
            result = function(self, *args, **kwargs)
        except (Exception, KeyboardInterrupt) as error:
            self.store.log(function.__name__, f"stopped: {type(error).__name__}")
            raise
        self.store.log(function.__name__, result or "finished")
        return result

    return wrapper


def run_menu(title, actions, back_key="0", back_label="Back to main menu", initial_action=None):
    while True:
        try:
            if initial_action is not None:
                action = initial_action
                initial_action = None
                action()
            print(f"\n{title}\n")
            for key, (label, action) in actions.items():
                print(f"{key}. {label}")
            print(f"{back_key}. {back_label}")
            choice = input("Choose an option: ").strip()
            if choice == back_key:
                return
            if choice not in actions:
                print("That option is not available. Please try again.")
                continue
            actions[choice][1]()
        except KeyboardInterrupt:
            print("\nAction interrupted. Saved restoration data is kept.")
        except (ToolError, OSError, ValueError, psutil.Error) as error:
            print(f"Action could not finish: {error}")
