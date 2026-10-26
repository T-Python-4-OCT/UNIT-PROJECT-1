from dataclasses import (
    asdict,
    dataclass
)

from tripmate.core.colors import (
    error,
    success
)

from tripmate.core.utils import (
    format_money,
    parse_date
)


@dataclass
class Trip:

    trip_id: int
    country: str
    city: str
    start_date: str
    end_date: str
    budget: float


    @property
    def days(self) -> int:

        try:

            delta = (
                parse_date(
                    self.end_date
                )
                -
                parse_date(
                    self.start_date
                )
            )

        except ValueError:

            return 1

        return max(
            delta.days + 1,
            1
        )


    def display_info(self) -> str:

        return (
            f"Trip ID: {self.trip_id}\n"
            f"Destination: "
            f"{self.city}, {self.country}\n"
            f"Start Date: {self.start_date}\n"
            f"End Date: {self.end_date}\n"
            f"Budget: "
            f"{format_money(self.budget)}"
        )


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
            trip_id=int(
                data["trip_id"]
            ),
            country=str(
                data["country"]
            ),
            city=str(
                data["city"]
            ),
            start_date=str(
                data["start_date"]
            ),
            end_date=str(
                data["end_date"]
            ),
            budget=float(
                data["budget"]
            )
        )


def create_trip(
    trips: list,
    trip_id: int,
    country: str,
    city: str,
    start_date: str,
    end_date: str,
    budget: float
):

    trip = Trip(
        trip_id,
        country,
        city,
        start_date,
        end_date,
        budget
    )

    trips.append(
        trip
    )

    success(
        "\nTrip created successfully."
    )

    success(
        f"Trip ID: {trip_id}"
    )

    return trip


def search_trip(
    trips: list,
    trip_id: int
):

    for trip in trips:

        if trip.trip_id == trip_id:

            return trip

    return None


def update_country(
    trip: Trip,
    country: str
):

    trip.country = country

    success(
        "Country updated successfully."
    )


def update_city(
    trip: Trip,
    city: str
):

    trip.city = city

    success(
        "City updated successfully."
    )


def update_dates(
    trip: Trip,
    start_date: str,
    end_date: str
):

    trip.start_date = start_date
    trip.end_date = end_date

    success(
        "Trip dates updated successfully."
    )


def update_budget(
    trip: Trip,
    budget: float
):

    trip.budget = budget

    success(
        "Budget updated successfully."
    )


def delete_trip(
    trips: list,
    expenses: list,
    trip_id: int
) -> bool:

    trip = search_trip(
        trips,
        trip_id
    )


    if trip is None:

        error(
            "Trip not found."
        )

        return False


    expenses[:] = [
        expense
        for expense in expenses
        if expense.trip_id != trip_id
    ]


    trips.remove(
        trip
    )


    success(
        "Trip and all related expenses "
        "deleted successfully."
    )

    return True