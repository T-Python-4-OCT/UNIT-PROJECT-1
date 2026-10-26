"""Reading and writing TripMate JSON data."""

import json
import os
import tempfile

from tripmate.core.colors import (
    warning
)

from tripmate.core.config import (
    DATA_FOLDER,
    EXPENSES_FILE,
    TRIPS_FILE
)

from tripmate.models.expenses import (
    Expense
)

from tripmate.models.trip import (
    Trip
)


TRIPS_SPEC = {
    "path": TRIPS_FILE,
    "items": "trips",
    "counter": "next_trip_id",
    "id": "trip_id",
}


EXPENSES_SPEC = {
    "path": EXPENSES_FILE,
    "items": "expenses",
    "counter": "next_expense_id",
    "id": "expense_id",
}


def _max_id(
    items: list,
    id_key: str
) -> int:

    ids = []


    for item in items:

        try:

            ids.append(
                int(
                    item[id_key]
                )
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            continue


    return max(
        ids,
        default=0
    )


def _write_json(
    path,
    data
):

    DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )


    file_descriptor, temp_path = (
        tempfile.mkstemp(
            dir=DATA_FOLDER,
            suffix=".tmp"
        )
    )


    try:

        with os.fdopen(
            file_descriptor,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


        os.replace(
            temp_path,
            path
        )


    except BaseException:

        if os.path.exists(
            temp_path
        ):

            os.remove(
                temp_path
            )

        raise


def _read_json(
    path
):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )


    except json.JSONDecodeError:

        backup = path.with_suffix(
            ".corrupted.json"
        )


        os.replace(
            path,
            backup
        )


        warning(
            f"{path.name} was damaged. "
            f"A copy was saved as "
            f"{backup.name}."
        )


        return None


def initialize_storage():

    DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )


    for spec in (
        TRIPS_SPEC,
        EXPENSES_SPEC
    ):

        if not spec[
            "path"
        ].exists():

            _write_json(
                spec["path"],
                {
                    spec["counter"]: 1,
                    spec["items"]: []
                }
            )


def _load_collection(
    spec: dict
) -> dict:

    initialize_storage()


    data = _read_json(
        spec["path"]
    )


    # Support old JSON list format.
    if isinstance(
        data,
        list
    ):

        data = {
            spec["items"]: data
        }


    if not isinstance(
        data,
        dict
    ):

        data = {}


    items = data.get(
        spec["items"],
        []
    )


    if not isinstance(
        items,
        list
    ):

        items = []


    counter = data.get(
        spec["counter"],
        1
    )


    if (
        not isinstance(
            counter,
            int
        )
        or
        counter < 1
    ):

        counter = 1


    counter = max(
        counter,
        _max_id(
            items,
            spec["id"]
        ) + 1
    )


    return {
        spec["counter"]: counter,
        spec["items"]: items
    }


def _save_collection(
    spec: dict,
    items: list
):

    initialize_storage()


    if items:

        counter = max(
            _load_collection(
                spec
            )[
                spec["counter"]
            ],
            _max_id(
                items,
                spec["id"]
            ) + 1
        )


    else:

        counter = 1


    _write_json(
        spec["path"],
        {
            spec["counter"]: counter,
            spec["items"]: items
        }
    )


def _reserve_next_id(
    spec: dict,
    current_items: list
) -> int:

    data = _load_collection(
        spec
    )


    next_id = max(
        data[
            spec["counter"]
        ],
        _max_id(
            current_items,
            spec["id"]
        ) + 1
    )


    data[
        spec["counter"]
    ] = next_id + 1


    _write_json(
        spec["path"],
        data
    )


    return next_id


def load_trips() -> list:

    trips = []


    for trip_data in _load_collection(
        TRIPS_SPEC
    )[
        "trips"
    ]:

        try:

            trips.append(
                Trip.from_dict(
                    trip_data
                )
            )


        except (
            KeyError,
            TypeError,
            ValueError
        ):

            warning(
                "A damaged trip record "
                "was skipped."
            )


    return trips


def save_trips(
    trips: list
):

    _save_collection(
        TRIPS_SPEC,
        [
            trip.to_dict()
            for trip in trips
        ]
    )


def get_next_trip_id(
    trips: list = None
) -> int:

    current = (
        [
            trip.to_dict()
            for trip in trips
        ]
        if trips
        else []
    )


    return _reserve_next_id(
        TRIPS_SPEC,
        current
    )


def load_expenses() -> list:

    expenses = []


    for expense_data in _load_collection(
        EXPENSES_SPEC
    )[
        "expenses"
    ]:

        try:

            expenses.append(
                Expense.from_dict(
                    expense_data
                )
            )


        except (
            KeyError,
            TypeError,
            ValueError
        ):

            warning(
                "A damaged expense record "
                "was skipped."
            )


    return expenses


def save_expenses(
    expenses: list
):

    _save_collection(
        EXPENSES_SPEC,
        [
            expense.to_dict()
            for expense in expenses
        ]
    )


def get_next_expense_id(
    expenses: list = None
) -> int:

    current = (
        [
            expense.to_dict()
            for expense in expenses
        ]
        if expenses
        else []
    )


    return _reserve_next_id(
        EXPENSES_SPEC,
        current
    )