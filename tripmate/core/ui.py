"""Reusable CLI user-interface helpers."""

from tripmate.core.colors import ai

from tripmate.core.validation import (
    get_menu_choice
)


def print_menu(
    title: str,
    options: list
):

    print(
        "\n================================"
    )

    print(
        f"   {title}"
    )

    print(
        "================================"
    )

    for index, option in enumerate(
        options,
        start=1
    ):

        print(
            f"{index}. {option}"
        )


def choose_from(
    title: str,
    options: dict,
    message: str
) -> str:

    ai(
        f"\n{title}"
    )

    for number, label in options.items():

        print(
            f"{number}. {label}"
        )

    choice = get_menu_choice(
        message,
        1,
        len(options)
    )

    return options[
        choice
    ]