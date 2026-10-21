"""Safe user input: the program never crashes because of a wrong answer."""

from cinema.ui.display import print_error


def ask_number(prompt: str, minimum: int, maximum: int) -> int:
    """Keep asking until the user types a whole number between minimum and maximum."""
    while True:
        text = input(prompt).strip()
        try:
            number = int(text)
        except ValueError:
            print_error("Please type a number.")
            continue
        if number < minimum or number > maximum:
            print_error(f"Please choose a number from {minimum} to {maximum}.")
            continue
        return number


def ask_menu(options: list[str], prompt: str = "Choose a number: ") -> int:
    """Print numbered options and return the chosen number (starting from 1)."""
    for number, option in enumerate(options, start=1):
        print(f"  {number}. {option}")
    print()
    return ask_number(prompt, 1, len(options))
