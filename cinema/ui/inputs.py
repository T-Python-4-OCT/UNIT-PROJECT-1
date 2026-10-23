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


def ask_name() -> str:
    """Full name: letters and spaces only, at least 3 letters."""
    while True:
        name = " ".join(input("Enter your full name: ").split())
        if len(name) < 3:
            print_error("Name must be at least 3 letters.")
        elif not name.replace(" ", "").isalpha():
            print_error("Name must contain letters only.")
        else:
            return name.title()


def ask_yes_no(question: str) -> bool:
    """Recursive: if the answer is not yes/no, the function calls itself again."""
    answer = input(f"{question} (yes/no): ").strip().lower()
    if answer in ("yes", "y"):
        return True
    if answer in ("no", "n"):
        return False
    print_error("Please type yes or no.")
    return ask_yes_no(question)


def ask_seat() -> str:
    """Turn inputs like 'b5', 'B-5' or 'b 5' into 'B5'."""
    text = input("\nEnter a seat (example: B5) or Q to stop: ")
    return text.upper().replace("-", "").replace(" ", "")
