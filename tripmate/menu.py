"""TripMate main application menu."""

from tripmate.workflows.ai_workflow import (
    ai_recommendation_workflow
)

from tripmate.core.colors import (
    warning
)

from tripmate.reports import (
    display_all_trips
)

from tripmate.workflows.trip_workflows import (
    create_trip_workflow,
    manage_trip_workflow
)

from tripmate.core.ui import (
    print_menu
)

from tripmate.core.validation import (
    get_menu_choice
)


def run_main_menu(
    trips: list,
    expenses: list
):

    options = [
        "Create Trip",
        "My Trips",
        "Manage Trip",
        "AI Travel Planner",
        "Exit"
    ]


    while True:

        print_menu(
            "TRIPMATE",
            options
        )


        choice = get_menu_choice(
            "Enter your choice: ",
            1,
            len(options)
        )


        if choice == 1:

            create_trip_workflow(
                trips
            )


        elif choice == 2:

            display_all_trips(
                trips,
                expenses
            )


        elif choice == 3:

            manage_trip_workflow(
                trips,
                expenses
            )


        elif choice == 4:

            ai_recommendation_workflow(
                trips
            )


        elif choice == 5:

            warning(
                "\nProgram ended."
            )

            break