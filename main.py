import sys

import config
from cli import ui
from cli.customer import run_customer
from cli.manager import run_manager


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print()
    ui.box(["Reservation System"], config.RESTAURANT_NAME)
    while True:
        choice = ui.menu("Main Menu", ["Customer", "Manager"], "Exit")
        if choice is None:
            print("Goodbye!")
            break
        elif choice == 0:
            run_customer()
        else:
            run_manager()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
