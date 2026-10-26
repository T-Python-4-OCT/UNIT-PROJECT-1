"""Shared Rich console and colored messages."""

from rich.console import Console


console = Console()


def _print(
    message: str,
    style: str
):

    console.print(
        message,
        style=style,
        markup=False,
        highlight=False
    )


def success(
    message: str
):

    _print(
        message,
        "green"
    )


def warning(
    message: str
):

    _print(
        message,
        "yellow"
    )


def error(
    message: str
):

    _print(
        message,
        "red"
    )


def info(
    message: str
):

    _print(
        message,
        "cyan"
    )


def ai(
    message: str
):

    _print(
        message,
        "blue"
    )