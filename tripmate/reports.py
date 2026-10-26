import csv

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from tripmate.core.colors import (
    console,
    error,
    warning
)

from tripmate.core.config import (
    BUDGET_WARNING_PERCENT,
    EXPORT_FOLDER
)

from tripmate.models.expenses import (
    build_expenses_table,
    calculate_category_totals,
    calculate_total_expenses,
    get_trip_expenses
)

from tripmate.core.utils import (
    format_money,
    safe_percentage
)


def _budget_summary(
    trip,
    expenses: list
):

    spent = calculate_total_expenses(
        expenses,
        trip.trip_id
    )

    remaining = (
        trip.budget - spent
    )

    percentage = safe_percentage(
        spent,
        trip.budget
    )


    return (
        spent,
        remaining,
        percentage
    )


def _percentage_color(
    percentage: float
) -> str:

    if percentage >= 100:

        return "red"


    if percentage >= BUDGET_WARNING_PERCENT:

        return "yellow"


    return "green"


def _colored(
    text: str,
    color: str
) -> str:

    return (
        f"[{color}]"
        f"{text}"
        f"[/{color}]"
    )


def _destination(
    trip
) -> str:

    return escape(
        f"{trip.city}, "
        f"{trip.country}"
    )


def _budget_message(
    percentage: float
):

    if percentage >= 100:

        console.print(
            "[bold red]"
            "You have exceeded "
            "your budget."
            "[/bold red]"
        )


    elif percentage >= BUDGET_WARNING_PERCENT:

        console.print(
            "[bold yellow]"
            f"You have used more than "
            f"{BUDGET_WARNING_PERCENT}% "
            f"of your budget."
            "[/bold yellow]"
        )


def display_all_trips(
    trips: list,
    expenses: list
):

    if not trips:

        warning(
            "No trips found."
        )

        return


    table = Table(
        title="My Trips",
        show_header=True,
        header_style="bold cyan"
    )


    table.add_column(
        "ID",
        justify="center"
    )

    table.add_column(
        "Destination"
    )

    table.add_column(
        "Dates",
        justify="center"
    )

    table.add_column(
        "Budget",
        justify="right"
    )

    table.add_column(
        "Spent",
        justify="right"
    )

    table.add_column(
        "Remaining",
        justify="right"
    )

    table.add_column(
        "Used",
        justify="right"
    )


    for trip in trips:

        spent, remaining, percentage = (
            _budget_summary(
                trip,
                expenses
            )
        )


        remaining_color = (
            "red"
            if remaining < 0
            else "green"
        )


        table.add_row(
            str(
                trip.trip_id
            ),
            _destination(
                trip
            ),
            (
                f"{trip.start_date}\n"
                f"{trip.end_date}"
            ),
            format_money(
                trip.budget
            ),
            format_money(
                spent
            ),
            _colored(
                format_money(
                    remaining
                ),
                remaining_color
            ),
            _colored(
                f"{percentage:.1f}%",
                _percentage_color(
                    percentage
                )
            )
        )


    console.print()

    console.print(
        table
    )


def display_trip_details(
    trip,
    expenses: list
):

    spent, remaining, percentage = (
        _budget_summary(
            trip,
            expenses
        )
    )


    details = (
        f"[bold]Trip ID:[/bold] "
        f"{trip.trip_id}\n"

        f"[bold]Destination:[/bold] "
        f"{_destination(trip)}\n"

        f"[bold]Start Date:[/bold] "
        f"{trip.start_date}\n"

        f"[bold]End Date:[/bold] "
        f"{trip.end_date}\n"

        f"[bold]Duration:[/bold] "
        f"{trip.days} day(s)\n\n"

        f"[bold]Budget:[/bold] "
        f"{format_money(trip.budget)}\n"

        f"[bold]Spent:[/bold] "
        f"{format_money(spent)}\n"

        f"[bold]Remaining:[/bold] "
        f"{format_money(remaining)}\n"

        f"[bold]Budget Used:[/bold] "
        f"{percentage:.1f}%"
    )


    console.print()


    console.print(
        Panel(
            details,
            title="Trip Details",
            border_style="cyan"
        )
    )


    if remaining < 0:

        console.print(
            "[bold red]"
            "Warning: You are over budget!"
            "[/bold red]"
        )


    trip_expenses = get_trip_expenses(
        expenses,
        trip.trip_id
    )


    if not trip_expenses:

        console.print(
            "\n[yellow]"
            "No expenses recorded."
            "[/yellow]"
        )

        return


    console.print()


    console.print(
        build_expenses_table(
            trip_expenses
        )
    )


def display_trip_report(
    trip,
    expenses: list
):

    trip_expenses = get_trip_expenses(
        expenses,
        trip.trip_id
    )


    spent, remaining, percentage = (
        _budget_summary(
            trip,
            expenses
        )
    )


    summary = Table(
        title="Trip Report",
        header_style="bold cyan"
    )


    summary.add_column(
        "Destination"
    )

    summary.add_column(
        "Budget",
        justify="right"
    )

    summary.add_column(
        "Spent",
        justify="right"
    )

    summary.add_column(
        "Remaining",
        justify="right"
    )

    summary.add_column(
        "Used",
        justify="right"
    )


    summary.add_row(
        _destination(
            trip
        ),
        format_money(
            trip.budget
        ),
        format_money(
            spent
        ),
        format_money(
            remaining
        ),
        f"{percentage:.1f}%"
    )


    console.print()

    console.print(
        summary
    )


    if not trip_expenses:

        console.print(
            "\n[yellow]"
            "No expenses available "
            "for analysis."
            "[/yellow]"
        )

        return


    category_totals = (
        calculate_category_totals(
            expenses,
            trip.trip_id
        )
    )


    breakdown = Table(
        title="Expense Breakdown",
        header_style="bold cyan"
    )


    breakdown.add_column(
        "Category"
    )

    breakdown.add_column(
        "Amount",
        justify="right"
    )

    breakdown.add_column(
        "Share",
        justify="right"
    )


    for category, amount in sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):

        breakdown.add_row(
            escape(
                category
            ),
            format_money(
                amount
            ),
            (
                f"{safe_percentage(amount, spent):.1f}%"
            )
        )


    console.print()

    console.print(
        breakdown
    )


    highest_expense = max(
        trip_expenses,
        key=lambda expense: expense.amount
    )


    highest_category = max(
        category_totals,
        key=category_totals.get
    )


    days = trip.days


    highlights = (
        f"[bold]Highest Expense:[/bold]\n"
        f"{escape(highest_expense.title)} - "
        f"{format_money(highest_expense.amount)}\n\n"

        f"[bold]Highest Spending Category:[/bold]\n"
        f"{escape(highest_category)} - "
        f"{format_money(category_totals[highest_category])}\n\n"

        f"[bold]Planned Daily Budget:[/bold]\n"
        f"{format_money(trip.budget / days)}\n\n"

        f"[bold]Expense per Planned Trip Day:[/bold]\n"
        f"{format_money(spent / days)}"
    )


    console.print()


    console.print(
        Panel(
            highlights,
            title="Highlights",
            border_style="cyan"
        )
    )


    _budget_message(
        percentage
    )


def _safe_cell(
    value
):

    text = str(
        value
    )


    if (
        text
        and
        text[0] in (
            "=",
            "+",
            "-",
            "@"
        )
    ):

        return "'" + text


    return text


def export_trip_to_csv(
    trip,
    expenses: list
):

    trip_expenses = (
        get_trip_expenses(
            expenses,
            trip.trip_id
        )
    )


    try:

        EXPORT_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )


        path = (
            EXPORT_FOLDER
            /
            f"trip_{trip.trip_id}.csv"
        )


        with open(
            path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(
                file
            )


            writer.writerow(
                [
                    "Trip",
                    _safe_cell(
                        f"{trip.city}, "
                        f"{trip.country}"
                    )
                ]
            )


            writer.writerow(
                [
                    "Dates",
                    (
                        f"{trip.start_date} "
                        f"to {trip.end_date}"
                    )
                ]
            )


            writer.writerow(
                [
                    "Budget",
                    trip.budget
                ]
            )


            writer.writerow(
                []
            )


            writer.writerow(
                [
                    "ID",
                    "Title",
                    "Category",
                    "Date",
                    "Amount"
                ]
            )


            for expense in trip_expenses:

                writer.writerow(
                    [
                        expense.expense_id,
                        _safe_cell(
                            expense.title
                        ),
                        _safe_cell(
                            expense.category
                        ),
                        expense.date,
                        expense.amount
                    ]
                )


            writer.writerow(
                []
            )


            writer.writerow(
                [
                    "",
                    "",
                    "",
                    "Total",
                    calculate_total_expenses(
                        expenses,
                        trip.trip_id
                    )
                ]
            )


    except OSError:

        error(
            "Could not write "
            "the export file."
        )

        return None


    return path