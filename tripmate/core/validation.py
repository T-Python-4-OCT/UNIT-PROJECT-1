import math
import re

from datetime import (
    date,
    datetime,
    timedelta
)

from tripmate.core.colors import (
    error
)

from tripmate.core.config import (
    EXPENSE_CATEGORIES,
    MAX_YEARS_AHEAD
)

from tripmate.core.utils import (
    DATE_FORMAT,
    parse_date
)


def get_text_input(
    message: str,
    min_length: int = 2
) -> str:

    while True:

        value = input(
            message
        ).strip()


        if not value:

            error(
                "Input cannot be empty."
            )

            continue


        if len(
            value
        ) < min_length:

            error(
                "Input is too short."
            )

            continue


        if not any(
            character.isalpha()
            for character in value
        ):

            error(
                "Please enter a valid "
                "text value."
            )

            continue


        return value


def _get_number(
    message: str,
    cast,
    allow_zero: bool
):

    while True:

        raw = input(
            message
        ).strip().replace(
            ",",
            ""
        )


        try:

            value = cast(
                raw
            )


        except ValueError:

            error(
                "Please enter a valid number."
            )

            continue


        if not math.isfinite(
            value
        ):

            error(
                "Please enter a valid number."
            )

            continue


        if (
            allow_zero
            and
            value < 0
        ):

            error(
                "Value cannot be negative."
            )

            continue


        if (
            not allow_zero
            and
            value <= 0
        ):

            error(
                "Value must be greater than 0."
            )

            continue


        return value


def get_positive_float(
    message: str
) -> float:

    return _get_number(
        message,
        float,
        allow_zero=False
    )


def get_positive_int(
    message: str
) -> int:

    return _get_number(
        message,
        int,
        allow_zero=False
    )


def get_non_negative_int(
    message: str
) -> int:

    return _get_number(
        message,
        int,
        allow_zero=True
    )


def get_menu_choice(
    message: str,
    minimum: int,
    maximum: int
) -> int:

    while True:

        try:

            choice = int(
                input(
                    message
                ).strip()
            )


        except ValueError:

            error(
                "Please enter a number only."
            )

            continue


        if (
            choice < minimum
            or
            choice > maximum
        ):

            error(
                f"Please choose from "
                f"{minimum} to {maximum}."
            )

            continue


        return choice


def get_yes_no(
    message: str
) -> bool:

    while True:

        answer = input(
            message
        ).strip().lower()


        if answer in (
            "y",
            "yes"
        ):

            return True


        if answer in (
            "n",
            "no"
        ):

            return False


        error(
            "Please enter y or n."
        )


def get_date(
    message: str,
    allow_past: bool = False,
    allow_future: bool = True,
    default: str = None
) -> str:

    accepted_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]

    while True:

        date_input = input(
            message
        ).strip()

        date_input = date_input.replace(
            "\\",
            "/"
        )


        if (
            not date_input
            and
            default is not None
        ):

            return default


        entered_date = None


        for date_format in accepted_formats:

            try:

                entered_date = datetime.strptime(
                    date_input,
                    date_format
                ).date()

                break

            except ValueError:

                continue


        if entered_date is None:

            error(
                "Invalid date. "
                "Examples: "
                "2026-12-01, "
                "2026/12/01, "
                "01-12-2026 or "
                "01/12/2026"
            )

            continue


        today = date.today()


        if (
            entered_date < today
            and
            not allow_past
        ):

            error(
                "Date cannot be in the past."
            )

            continue


        if (
            entered_date > today
            and
            not allow_future
        ):

            error(
                "Date cannot be in the future."
            )

            continue


        if (
            entered_date.year
            >
            today.year + MAX_YEARS_AHEAD
        ):

            error(
                f"Trip date cannot be more "
                f"than {MAX_YEARS_AHEAD} "
                f"years in the future."
            )

            continue


        return entered_date.strftime(
            DATE_FORMAT
        )

    accepted_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]

    while True:

        date_input = input(
            message
        ).strip()


        if (
            not date_input
            and
            default is not None
        ):

            return default


        entered_date = None


        for date_format in accepted_formats:

            try:

                entered_date = datetime.strptime(
                    date_input,
                    date_format
                ).date()

                break

            except ValueError:

                continue


        if entered_date is None:

            error(
                "Invalid date. "
                "Examples: "
                "2026-12-01 or 01/12/2026"
            )

            continue


        today = date.today()


        if (
            entered_date < today
            and
            not allow_past
        ):

            error(
                "Date cannot be in the past."
            )

            continue


        if (
            entered_date > today
            and
            not allow_future
        ):

            error(
                "Date cannot be in the future."
            )

            continue


        if (
            entered_date.year
            >
            today.year + MAX_YEARS_AHEAD
        ):

            error(
                f"Trip date cannot be more "
                f"than {MAX_YEARS_AHEAD} "
                f"years in the future."
            )

            continue


        return entered_date.strftime(
            DATE_FORMAT
        )

    while True:

        date_input = input(
            message
        ).strip()


        if (
            not date_input
            and
            default is not None
        ):

            return default


        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}",
            date_input
        ):

            error(
                "Please use this format: "
                "YYYY-MM-DD"
            )

            continue


        try:

            entered_date = parse_date(
                date_input
            )


        except ValueError:

            error(
                "Invalid date."
            )

            continue


        today = date.today()


        if (
            entered_date < today
            and
            not allow_past
        ):

            error(
                "Date cannot be in the past."
            )

            continue


        if (
            entered_date > today
            and
            not allow_future
        ):

            error(
                "Date cannot be in the future."
            )

            continue


        if (
            entered_date.year
            >
            today.year + MAX_YEARS_AHEAD
        ):

            error(
                f"Trip date cannot be more "
                f"than {MAX_YEARS_AHEAD} "
                f"years in the future."
            )

            continue


        return date_input


def get_trip_dates():

    start_date = get_date(
        "Enter start date "
        "(YYYY-MM-DD): "
    )


    start = parse_date(
        start_date
    )


    while True:

        end_date = get_date(
            "Enter end date "
            "(YYYY-MM-DD): "
        )


        if parse_date(
            end_date
        ) < start:

            error(
                "End date cannot be "
                "before start date."
            )

            continue


        return (
            start_date,
            end_date
        )


def calculate_end_date(
    start_date: str,
    days: int
) -> str:

    end = (
        parse_date(
            start_date
        )
        +
        timedelta(
            days=days - 1
        )
    )


    return end.strftime(
        DATE_FORMAT
    )


def get_expense_category() -> str:

    print(
        "\nChoose expense category:"
    )


    for index, category in enumerate(
        EXPENSE_CATEGORIES,
        start=1
    ):

        print(
            f"{index}. {category}"
        )


    choice = get_menu_choice(
        "Enter category number: ",
        1,
        len(
            EXPENSE_CATEGORIES
        )
    )


    return EXPENSE_CATEGORIES[
        choice - 1
    ]