import questionary
from questionary import Choice, Style
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

def print_header(title, subtitle=""):
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]", border_style="cyan"))

def print_success(message):
    console.print(f"[bold green]✔ {message}[/bold green]")

def print_error(message):
    console.print(f"[bold red]✖ {message}[/bold red]")

def print_info(message):
    console.print(f"[bold yellow]ℹ {message}[/bold yellow]")

def prompt_select(message, choices):
    custom_style = Style([
        ("qmark", "fg:yellow bold"),
        ("question", "fg:white bold"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "bold"),
    ])
    return questionary.select(message, choices=choices, style=custom_style).ask()

def prompt_required_text(message, default_value=""):
    custom_style = Style([
        ("qmark", "fg:yellow bold"),
        ("question", "fg:white bold"),
        ("answer", "fg:cyan bold"),
    ])
    return questionary.text(message, default=default_value, style=custom_style).ask()

def prompt_confirm(message="Are you sure you want to delete this item?"):
    custom_style = Style([
        ("qmark", "fg:yellow bold"),
        ("question", "fg:white bold"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "bold"),
    ])
    choices = [
        Choice(title=[("fg:white", "No, Cancel (Keep item)")], value=False),
        Choice(title=[("fg:ansired bold", "Yes, Delete Successfully")], value=True),
    ]
    result = questionary.select(
        message,
        choices=choices,
        style=custom_style
    ).ask()
    return bool(result)

def confirm_delete(message="Are you sure you want to delete this item?"):
    return prompt_confirm(message)

def prompt_password(message):
    custom_style = Style([
        ("qmark", "fg:yellow bold"),
        ("question", "fg:white bold"),
        ("answer", "fg:cyan bold"),
    ])
    return questionary.password(message, style=custom_style).ask()

def prompt_positive_int(message, default_val=1, default_value=None):
    if default_value is not None:
        default_val = default_value
    while True:
        val = prompt_required_text(message, default_value=str(default_val))
        try:
            num = int(val)
            if num > 0:
                return num
            print_error("Please enter a positive integer greater than 0.")
        except ValueError:
            print_error("Please enter a valid integer.")

def show_spinner(text="Loading..."):
    with console.status(f"[bold cyan]{text}[/bold cyan]", spinner="dots"):
        time.sleep(0.5)

def render_progress_bar(percentage, width=14):
    filled = int(round((percentage / 100) * width))
    filled = max(0, min(width, filled))
    bar = "█" * filled + "░" * (width - filled)
    color = "green" if percentage >= 80 else ("cyan" if percentage >= 50 else "yellow")
    return f"[{color}]{bar} {percentage}%[/{color}]"