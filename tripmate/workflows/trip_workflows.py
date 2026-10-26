"""Interactive workflows for creating and managing trips."""

from tripmate.core.colors import (
    error,
    info,
    success,
    warning
)

from tripmate.workflows.expense_workflows import (
    add_expense_workflow,
    delete_expense_workflow,
    edit_expense_workflow
)

from tripmate.models.expenses import (
    calculate_total_expenses
)

from tripmate.workflows.location_workflow import (
    get_confirmed_location
)

from tripmate.reports import (
    display_all_trips,
    display_trip_details,
    display_trip_report,
    export_trip_to_csv
)

from tripmate.services.storage import (
    get_next_trip_id,
    save_expenses,
    save_trips
)

from tripmate.models.trip import (
    create_trip,
    delete_trip,
    search_trip,
    update_budget,
    update_city,
    update_country,
    update_dates
)

from tripmate.core.ui import (
    print_menu
)

from tripmate.core.utils import (
    format_money
)

from tripmate.core.validation import (
    get_menu_choice,
    get_non_negative_int,
    get_positive_float,
    get_trip_dates,
    get_yes_no
)

from tripmate.services.weather import (
    display_weather_for_trip
)


def create_trip_workflow(
    trips: list
):

    info(
        "\n--- Create Trip ---"
    )


    destination = (
        get_confirmed_location(
            "Destination"
        )
    )


    if destination is None:

        return


    start_date, end_date = (
        get_trip_dates()
    )


    budget = get_positive_float(
        "Enter budget: "
    )


    trip_id = (
        get_next_trip_id(
            trips
        )
    )


    create_trip(
        trips,
        trip_id,
        destination[
            "country"
        ],
        destination[
            "city"
        ],
        start_date,
        end_date,
        budget
    )


    save_trips(
        trips
    )


def update_trip_menu(
    trip,
    trips: list,
    expenses: list
):

    while True:

        print_menu(
            "Update Trip",
            [
                "Destination",
                "Dates",
                "Budget",
                "Back"
            ]
        )


        choice = get_menu_choice(
            "What do you want to update? ",
            1,
            4
        )


        if choice == 1:

            destination = (
                get_confirmed_location(
                    "New Destination"
                )
            )


            if destination is None:

                continue


            update_country(
                trip,
                destination[
                    "country"
                ]
            )


            update_city(
                trip,
                destination[
                    "city"
                ]
            )


            save_trips(
                trips
            )


        elif choice == 2:

            start_date, end_date = (
                get_trip_dates()
            )


            update_dates(
                trip,
                start_date,
                end_date
            )


            save_trips(
                trips
            )


        elif choice == 3:

            budget = get_positive_float(
                "Enter new budget: "
            )


            current_spent = (
                calculate_total_expenses(
                    expenses,
                    trip.trip_id
                )
            )


            if budget < current_spent:

                warning(
                    "\nNew budget is lower "
                    "than current spending."
                )


                print(
                    f"Current spending: "
                    f"{format_money(current_spent)}"
                )


                print(
                    f"New budget: "
                    f"{format_money(budget)}"
                )


                confirm = get_yes_no(
                    "Continue? (y/n): "
                )


                if not confirm:

                    warning(
                        "Budget update cancelled."
                    )

                    continue


            update_budget(
                trip,
                budget
            )


            save_trips(
                trips
            )


        elif choice == 4:

            break


def export_report_workflow(
    trip,
    expenses: list
):

    path = export_trip_to_csv(
        trip,
        expenses
    )


    if path is not None:

        success(
            f"Report saved to: {path}"
        )


def manage_trip_workflow(
    trips: list,
    expenses: list
):

    if not trips:

        warning(
            "No trips available."
        )

        return


    display_all_trips(
        trips,
        expenses
    )


    print(
        "\nEnter 0 to go back."
    )


    trip_id = get_non_negative_int(
        "Enter trip ID: "
    )


    if trip_id == 0:

        return


    trip = search_trip(
        trips,
        trip_id
    )


    if trip is None:

        error(
            "Trip not found."
        )

        return


    options = [
        "View Trip Details",
        "Update Trip",
        "Add Expense",
        "Edit Expense",
        "Delete Expense",
        "Trip Report",
        "Export Report (CSV)",
        "Check Trip Weather",
        "Delete Trip",
        "Back"
    ]


    while True:

        print_menu(
            (
                f"{trip.city}, "
                f"{trip.country}"
            ),
            options
        )


        choice = get_menu_choice(
            "Enter your choice: ",
            1,
            len(options)
        )


        if choice == 1:

            display_trip_details(
                trip,
                expenses
            )


        elif choice == 2:

            update_trip_menu(
                trip,
                trips,
                expenses
            )


        elif choice == 3:

            add_expense_workflow(
                trip,
                expenses
            )


        elif choice == 4:

            edit_expense_workflow(
                trip,
                expenses
            )


        elif choice == 5:

            delete_expense_workflow(
                trip,
                expenses
            )


        elif choice == 6:

            display_trip_report(
                trip,
                expenses
            )


        elif choice == 7:

            export_report_workflow(
                trip,
                expenses
            )


        elif choice == 8:

            display_weather_for_trip(
                trip
            )


        elif choice == 9:

            display_trip_details(
                trip,
                expenses
            )


            warning(
                "\nDeleting this trip "
                "will also delete "
                "all its expenses."
            )


            confirm = get_yes_no(
                "Delete this trip? (y/n): "
            )


            if not confirm:

                warning(
                    "Delete cancelled."
                )

                continue


            deleted = delete_trip(
                trips,
                expenses,
                trip.trip_id
            )


            if deleted:

                save_trips(
                    trips
                )

                save_expenses(
                    expenses
                )

                break


        elif choice == 10:

            break