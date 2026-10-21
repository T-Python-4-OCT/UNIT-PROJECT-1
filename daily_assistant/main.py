from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from news import show_top_news, show_saudi_news, show_sports_news, show_technology_news
from ui import banner, console
from weather import show_weather

MENU = [
    ("1", "🌍", "Today's Top News", show_top_news),
    ("2", "🇸🇦", "Saudi Arabia News", show_saudi_news),
    ("3", "⚽", "Sports News", show_sports_news),
    ("4", "💻", "Technology News", show_technology_news),
    ("5", "🌤️", "Check Weather", show_weather),
    ("6", "🚪", "Exit", None),
]


def print_menu():
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan", justify="right")
    table.add_column()
    table.add_column()
    for key, icon, label, _ in MENU:
        table.add_row(key, icon, label)
    console.print(Panel(table, title="[bold]MENU[/]", border_style="cyan", expand=False, padding=(1, 3)))


def main():
    console.clear()
    banner()
    actions = {key: action for key, _, _, action in MENU}

    while True:
        print_menu()
        choice = Prompt.ask("[bold cyan]Enter your choice[/]", choices=list(actions), show_choices=False)

        if choice == "6":
            console.print("\n[bold green]Thank you for using Daily News & Weather! 👋[/]\n")
            break

        actions[choice]()
        console.print()
        Prompt.ask("[dim]Press Enter to return to the menu[/]", default="", show_default=False)
        console.clear()
        banner()


if __name__ == "__main__":
    main()