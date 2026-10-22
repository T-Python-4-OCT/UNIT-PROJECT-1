import time
import questionary
from colorama import init
from rich.console import Console
from rich.panel import Panel

init(autoreset=True)
console = Console()


def show_spinner(message="Loading...", duration=0.35):
    with console.status(f"[cyan]{message}[/cyan]", spinner="dots"):
        time.sleep(duration)


def print_header(title, subtitle=""):
    text = f"[bold cyan]{title}[/bold cyan]"
    if subtitle != "":
        text = text + f"\n[white]{subtitle}[/white]"
    console.print()
    console.print(Panel(text, expand=False, border_style="cyan"))


def prompt_select(prompt_message, choices):
    return questionary.select(prompt_message, choices=choices).ask()