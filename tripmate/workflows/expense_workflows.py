"""Interactive workflows for trip expenses."""

from tripmate.core.colors import (
    error,
    info,
    warning
)

from tripmate.models.expenses import (
    add_expense,
    calculate_total_expenses,
    delete_expense,
    display_trip_expenses,
    get_expense,
    get_trip_expenses,
    update_expense
)

from tripmate.services.storage import (
    get_next_expense_id,
    save_expenses
)

from tripmate.core.ui import (
    print_menu
)

from tripmate.core.utils import (
    format_money,
    today_str
)

from tripmate.core.validation import (
    get_date,
    get_expense_category,
    get_menu_choice,
    get_positive_float,
    get_positive_int,
    get_text_input,
    get_yes_no
)


def warn_if_over_budget(
    trip,
    expenses: list
):

    spent = calculate_total_expenses(
        expenses,
        trip.trip_id
    )

    if spent > trip.budget:

        warning(
            "Warning: this trip is "
            "over budget "
            f"({format_money(spent)} "
            f"of {format_money(trip.budget)})."
        )


def add_expense_workflow(
    trip,
    expenses: list
):

    info(
        "\n--- Add Expense ---"
    )


    print(
        f"Trip: "
        f"{trip.city}, "
        f"{trip.country}"
    )


    title = get_text_input(
        "Enter expense title: "
    )


    category = (
        get_expense_category()
    )


    amount = get_positive_float(
        "Enter amount: "
    )


    expense_date = get_date(
        (
            "Enter expense date "
            "(YYYY-MM-DD, "
            "press Enter for today): "
        ),
        allow_past=True,
        allow_future=False,
        default=today_str()
    )


    current_spent = (
        calculate_total_expenses(
            expenses,
            trip.trip_id
        )
    )


    remaining = (
        trip.budget
        - current_spent
    )


    if amount > remaining:

        warning(
            "\nThis expense exceeds "
            "your remaining budget."
        )


        print(
            f"Remaining budget: "
            f"{format_money(remaining)}"
        )


        print(
            f"Expense amount: "
            f"{format_money(amount)}"
        )


        confirm = get_yes_no(
            "Add it anyway? (y/n): "
        )


        if not confirm:

            warning(
                "Expense cancelled."
            )

            return


    expense_id = (
        get_next_expense_id(
            expenses
        )
    )


    add_expense(
        expenses,
        expense_id,
        trip.trip_id,
        title,
        category,
        amount,
        expense_date
    )


    save_expenses(
        expenses
    )


def select_expense(
    trip,
    expenses: list,
    action: str
):

    trip_expenses = (
        get_trip_expenses(
            expenses,
            trip.trip_id
        )
    )


    if not trip_expenses:

        warning(
            "This trip has no expenses."
        )

        return None


    display_trip_expenses(
        expenses,
        trip.trip_id
    )


    expense_id = get_positive_int(
        f"Enter expense ID "
        f"to {action}: "
    )


    expense = get_expense(
        expenses,
        trip.trip_id,
        expense_id
    )


    if expense is None:

        error(
            "That expense does not "
            "belong to this trip."
        )

        return None


    return expense


def edit_expense_workflow(
    trip,
    expenses: list
):

    info(
        "\n--- Edit Expense ---"
    )


    expense = select_expense(
        trip,
        expenses,
        "edit"
    )


    if expense is None:

        return


    print_menu(
        "Edit Expense",
        [
            "Title",
            "Category",
            "Amount",
            "Date",
            "Cancel"
        ]
    )


    choice = get_menu_choice(
        "What do you want to edit? ",
        1,
        5
    )


    if choice == 1:

        update_expense(
            expense,
            title=get_text_input(
                "Enter new title: "
            )
        )


    elif choice == 2:

        update_expense(
            expense,
            category=(
                get_expense_category()
            )
        )


    elif choice == 3:

        update_expense(
            expense,
            amount=get_positive_float(
                "Enter new amount: "
            )
        )


    elif choice == 4:

        update_expense(
            expense,
            date=get_date(
                "Enter new date "
                "(YYYY-MM-DD): ",
                allow_past=True,
                allow_future=False
            )
        )


    elif choice == 5:

        warning(
            "Edit cancelled."
        )

        return


    save_expenses(
        expenses
    )


    warn_if_over_budget(
        trip,
        expenses
    )


def delete_expense_workflow(
    trip,
    expenses: list
):

    info(
        "\n--- Delete Expense ---"
    )


    expense = select_expense(
        trip,
        expenses,
        "delete"
    )


    if expense is None:

        return


    print(
        "\nSelected Expense:"
    )


    print(
        f"{expense.title} | "
        f"{expense.category} | "
        f"{format_money(expense.amount)}"
    )


    confirm = get_yes_no(
        "Delete this expense? (y/n): "
    )


    if not confirm:

        warning(
            "Delete cancelled."
        )

        return


    deleted = delete_expense(
        expenses,
        trip.trip_id,
        expense.expense_id
    )


    if deleted:

        save_expenses(
            expenses
        )