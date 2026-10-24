import time
from rich.console import Console
from rich.panel import Panel
import questionary

console = Console()

def print_header(title, subtitle=""):
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]", border_style="cyan"))

def print_success(message):
    console.print(f"[bold green]✔ {message}[/bold green]")

def print_error(message):
    console.print(f"[bold red]✖ {message}[/bold red]")

def print_warning(message):
    console.print(f"[bold yellow]⚠ {message}[/bold yellow]")

def print_info(message):
    console.print(f"[bold blue]ℹ {message}[/bold blue]")

def prompt_required_text(prompt_text, default_value=None):
    while True:
        val = questionary.text(prompt_text, default=str(default_value) if default_value else "").ask()
        if val is not None and str(val).strip() != "":
            return str(val).strip()
        print_error("This field cannot be empty.")

def prompt_positive_int(prompt_text, default_value="3"):
    while True:
        val = questionary.text(prompt_text, default=str(default_value)).ask()
        try:
            num = int(val)
            if num >= 0:
                return num
            print_error("Please enter a valid number.")
        except ValueError:
            print_error("Invalid number. Please try again.")

def prompt_select(prompt_text, choices):
    cleaned_choices = []
    choice_map = {}
    
    for c in choices:
        clean_c = c.split(". ", 1)[1] if "." in c and c.split(". ", 1)[0].isdigit() else c
        cleaned_choices.append(clean_c)
        choice_map[clean_c] = c

    selected = questionary.select(
        prompt_text,
        choices=cleaned_choices,
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
        ])
    ).ask()

    if selected is None:
        return None
        
    return choice_map.get(selected, selected)

def prompt_checkbox(prompt_text, choices, checked_items=None):
    checked_items = checked_items or []
    q_choices = [
        questionary.Choice(title=c, value=c, checked=(c in checked_items))
        for c in choices
    ]
    return questionary.checkbox(
        prompt_text,
        choices=q_choices,
        style=questionary.Style([
            ('selected', 'fg:green bold'),
            ('pointer', 'fg:cyan bold'),
        ])
    ).ask()

def confirm_delete(item_name):
    """Display a red warning panel and ask for explicit delete confirmation."""
    console.print(
        Panel(
            f"[bold red]⚠ WARNING: You are about to permanently delete:[/bold red]\n[bold white]{item_name}[/bold white]",
            title="[bold red]Confirm Deletion[/bold red]",
            border_style="red"
        )
    )
    ans = questionary.select(
        "Are you sure you want to delete this item?",
        choices=[
            "No, Cancel and Keep Item",
            "Yes, Permanently Delete"
        ],
        style=questionary.Style([
            ('qmark', 'fg:red bold'),
            ('question', 'fg:red bold'),
            ('pointer', 'fg:red bold'),
            ('highlighted', 'fg:red bold'),
            ('selected', 'fg:red bold'),
        ])
    ).ask()
    return ans == "Yes, Permanently Delete"

def show_spinner(message="Loading..."):
    with console.status(f"[bold cyan]{message}[/bold cyan]"):
        time.sleep(0.4)


def prompt_password(prompt_text):
    while True:
        val = questionary.password(prompt_text).ask()
        if val is not None and str(val).strip() != "":
            return str(val).strip()
        print_error("Password cannot be empty.")