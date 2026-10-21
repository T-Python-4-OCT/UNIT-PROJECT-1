from colorama import init, Fore, Style
from tabulate import tabulate

init(autoreset=True)


def print_success(message):
    print(Fore.GREEN + f"[OK] {message}")


def print_error(message):
    print(Fore.RED + f"[ERROR] {message}")


def print_warning(message):
    print(Fore.YELLOW + f"[WARNING] {message}")


def print_info(message):
    print(Fore.CYAN + f"[INFO] {message}")


def print_title(message):
    print(Fore.CYAN + Style.BRIGHT + f"\n===== {message} =====")


def print_table(rows, headers):
    print(tabulate(rows, headers=headers, tablefmt="grid"))