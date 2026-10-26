from tripmate.menu import (
    run_main_menu
)

from tripmate.services.storage import (
    load_expenses,
    load_trips
)


def main():

    trips = load_trips()

    expenses = load_expenses()

    run_main_menu(
        trips,
        expenses
    )


if __name__ == "__main__":

    try:

        main()

    except (
        KeyboardInterrupt,
        EOFError
    ):

        print(
            "\n\nProgram ended."
        )