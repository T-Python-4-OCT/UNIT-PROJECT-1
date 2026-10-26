"""Printing helpers: clear screen, titles and colored messages."""

import os

from colorama import Fore, Style

WIDTH = 60


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_title(title: str) -> None:
    print(Fore.CYAN + "=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH + Style.RESET_ALL)


def print_step(number: int, total: int, title: str) -> None:
    """Clear the screen and show the booking step, e.g. 'Step 2/7 - Choose a cinema'."""
    clear_screen()
    print_title(f"Step {number}/{total} - {title}")


def print_success(message: str) -> None:
    print(Fore.GREEN + "✔ " + message + Style.RESET_ALL)


def print_error(message: str) -> None:
    print(Fore.RED + "✘ " + message + Style.RESET_ALL)


def print_info(message: str) -> None:
    print(Fore.YELLOW + message + Style.RESET_ALL)
