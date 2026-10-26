"""Small helpers shared by several modules."""

from datetime import (
    date,
    datetime
)

from tripmate.core.config import (
    CURRENCY
)


DATE_FORMAT = "%Y-%m-%d"


def format_money(
    amount: float
) -> str:

    return (
        f"{amount:,.2f} "
        f"{CURRENCY}"
    )


def safe_percentage(
    part: float,
    whole: float
) -> float:

    if whole <= 0:

        if part > 0:
            return 100.0

        return 0.0

    return (
        part / whole
    ) * 100


def parse_date(
    value: str
) -> date:

    return datetime.strptime(
        value,
        DATE_FORMAT
    ).date()


def today_str() -> str:

    return date.today().strftime(
        DATE_FORMAT
    )