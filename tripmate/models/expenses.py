from dataclasses import (
    asdict,
    dataclass
)

from rich.markup import escape
from rich.table import Table

from tripmate.core.colors import (
    console,
    error,
    success
)

from tripmate.core.config import (
    EXPENSE_CATEGORIES
)

from tripmate.core.utils import (
    format_money,
    today_str
)


@dataclass
class Expense:

    expense_id: int
    trip_id: int
    title: str
    category: str
    amount: float
    date: str = ""


    def to_dict(self) -> dict:

        return asdict(
            self
        )


    @classmethod
    def from_dict(
        cls,
        data: dict
    ):

        return cls(
            expense_id=int(
                data["expense_id"]
            ),
            trip_id=int(
                data["trip_id"]
            ),
            title=str(
                data["title"]
            ),
            category=str(
                data.get(
                    "category",
                    "Other"
                )
            ),
            amount=float(
                data["amount"]
            ),
            date=str(
                data.get(
                    "date",
                    ""
                )
            )
        )


def add_expense(
    expenses: list,
    expense_id: int,
    trip_id: int,
    title: str,
    category: str,
    amount: float,
    date: str = ""
):

    expense = Expense(
        expense_id=expense_id,
        trip_id=trip_id,
        title=title,
        category=category,
        amount=amount,
        date=date or today_str()
    )


    expenses.append(
        expense
    )


    success(
        "\nExpense added successfully."
    )

    success(
        f"Expense ID: {expense_id}"
    )


    return expense


def get_trip_expenses(
    expenses: list,
    trip_id: int
) -> list:

    return [
        expense
        for expense in expenses
        if expense.trip_id == trip_id
    ]


def get_expense(
    expenses: list,
    trip_id: int,
    expense_id: int
):

    for expense in expenses:

        if (
            expense.trip_id == trip_id
            and
            expense.expense_id == expense_id
        ):

            return expense

    return None


def calculate_total_expenses(
    expenses: list,
    trip_id: int
) -> float:

    return sum(
        expense.amount
        for expense in expenses
        if expense.trip_id == trip_id
    )


def calculate_category_totals(
    expenses: list,
    trip_id: int
) -> dict:

    totals = {}


    for expense in get_trip_expenses(
        expenses,
        trip_id
    ):

        totals[
            expense.category
        ] = (
            totals.get(
                expense.category,
                0
            )
            +
            expense.amount
        )


    return totals


def update_expense(
    expense: Expense,
    title: str = None,
    category: str = None,
    amount: float = None,
    date: str = None
):

    if title is not None:

        expense.title = title


    if category is not None:

        expense.category = category


    if amount is not None:

        expense.amount = amount


    if date is not None:

        expense.date = date


    success(
        "Expense updated successfully."
    )


def build_expenses_table(
    trip_expenses: list,
    title: str = "Expenses"
) -> Table:

    table = Table(
        title=title,
        header_style="bold cyan"
    )


    table.add_column(
        "ID",
        justify="center"
    )

    table.add_column(
        "Title"
    )

    table.add_column(
        "Category"
    )

    table.add_column(
        "Date",
        justify="center"
    )

    table.add_column(
        "Amount",
        justify="right"
    )


    for expense in trip_expenses:

        table.add_row(
            str(
                expense.expense_id
            ),
            escape(
                expense.title
            ),
            escape(
                expense.category
            ),
            expense.date or "-",
            format_money(
                expense.amount
            )
        )


    return table


def display_trip_expenses(
    expenses: list,
    trip_id: int
) -> bool:

    trip_expenses = (
        get_trip_expenses(
            expenses,
            trip_id
        )
    )


    if not trip_expenses:

        console.print(
            "[yellow]"
            "No expenses recorded "
            "for this trip."
            "[/yellow]"
        )

        return False


    console.print()

    console.print(
        build_expenses_table(
            trip_expenses
        )
    )

    return True


def delete_expense(
    expenses: list,
    trip_id: int,
    expense_id: int
) -> bool:

    expense = get_expense(
        expenses,
        trip_id,
        expense_id
    )


    if expense is None:

        error(
            "Expense not found "
            "for this trip."
        )

        return False


    expenses.remove(
        expense
    )


    success(
        "Expense deleted successfully."
    )

    return True