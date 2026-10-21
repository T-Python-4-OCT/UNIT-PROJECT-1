from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

console = Console()


def banner():
    title = Text("DAILY NEWS & WEATHER", style="bold white", justify="center")
    subtitle = Text("Your world, in one terminal", style="dim italic", justify="center")
    body = Text("\n").join([title, subtitle])
    console.print(Panel(Align.center(body), border_style="cyan", padding=(1, 4)))


def section(title, color="cyan"):
    console.print()
    console.rule(f"[bold {color}]{title}[/]", style=color)
    console.print()


def error(message):
    console.print(Panel(Text(message, style="red"), title="Error", border_style="red"))


def info(message):
    console.print(Panel(Text(message, style="yellow"), border_style="yellow"))