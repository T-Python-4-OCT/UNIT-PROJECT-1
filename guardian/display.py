"""How the app looks: the console, colors, the big title, and money formatting."""
import pyfiglet
import questionary
from rich.console import Console

console = Console()

# Blue colors for the lists so they match the title
MENU_STYLE = questionary.Style([
    ("qmark", "fg:#5c9dff bold"),
    ("pointer", "fg:#5c9dff bold"),
    ("highlighted", "fg:#5c9dff bold"),
    ("question", "bold"),
    ("answer", "fg:#5c9dff bold"),
])
POINTER = "➜"

# Blue shades from light to dark, one for each line of the big title
BLUE_GRADIENT = (
    "#a8cfff", "#9cc7ff", "#8bbcff", "#7ab3ff", "#6aa8ff", "#5c9dff",
    "#4f93fa", "#3f86f5", "#357aeb", "#2b6fe0", "#2566db", "#1f5fd6",
)


def show_banner():
    """Print the big blue title with a gradient, and the slogan under it."""
    lines = []
    for word in ("SUBSCRIPTION", "GUARDIAN"):
        art = pyfiglet.figlet_format(word, font="ansi_shadow", width=200)
        lines += [line for line in art.splitlines() if line.strip()]

    widest = max(len(line) for line in lines)

    # The big letters need a wide window, otherwise show a simple title
    if console.width < widest:
        console.print("[bold #5c9dff]SUBSCRIPTION GUARDIAN[/]")
        console.print("[dim]Keep your money safe[/dim]\n")
        return

    for line, color in zip(lines, BLUE_GRADIENT):
        console.print(line, style=f"bold {color}", highlight=False)
    console.print("Keep your money safe".center(widest), style="dim")
    console.print()


def money(amount: float) -> str:
    """Format money in a readable way: 23333 -> '23,333 SAR', 18.333 -> '18.33 SAR'."""
    amount = round(amount, 2)
    if amount == int(amount):
        return f"{int(amount):,} SAR"
    return f"{amount:,.2f} SAR"
