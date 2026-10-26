from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def banner():
    title = Text.assemble(
        ("DAILY ", "bold white"),
        ("NEWS", "bold bright_cyan"),
        (" & ", "bold white"),
        ("WEATHER", "bold bright_blue"),
    )
    subtitle = Text("Your Daily Information Dashboard", style="dim white")

    content = Table.grid(expand=True)
    content.add_column(justify="center", ratio=1)
    content.add_row(Align.center(title))
    content.add_row(Align.center(subtitle))

    console.print(Panel(content, border_style="bright_blue", padding=(1, 3)))


def section(title, color="cyan"):
    console.print()
    console.rule(f"[bold {color}]{title}[/]", style=color)
    console.print()


def error(message):
    console.print(Panel(Text(message, style="red"), title="Error", border_style="red"))


def info(message):
    console.print(Panel(Text(message, style="yellow"), border_style="yellow"))