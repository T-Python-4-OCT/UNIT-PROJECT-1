from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from news import NewsManager
from pdf_report import PDFReport
from ui import banner, console
from weather import WeatherManager

MENU = [
    ("1", "🌍", "Today's Top News"),
    ("2", "🇸🇦", "Saudi Arabia News"),
    ("3", "⚽", "Sports News"),
    ("4", "💻", "Technology News"),
    ("5", "🔎", "Search News by Keyword"),
    ("6", "🌤️", "Check Weather"),
    ("7", "📄", "Save PDF Report"),
    ("8", "🚪", "Exit"),
]


def print_menu():
    table = Table(
        show_header=False,
        show_edge=False,
        show_lines=True,
        padding=(0, 2),
        expand=True,
        border_style="dim cyan",
    )
    table.add_column(style="bold cyan", justify="right")
    table.add_column()
    table.add_column()

    for key, icon, label in MENU:
        table.add_row(key, icon, label)

    console.print(
        Panel(table, title="[bold]MAIN MENU[/]", border_style="cyan",
              expand=False, padding=(1, 3))
    )


def refresh_screen():
    console.clear()
    banner()


def main():
    news = NewsManager()
    weather = WeatherManager()
    pdf = PDFReport()

    news_sections = {}
    weather_data = None

    news_actions = {
        "1": ("World News", news.top_news),
        "2": ("Saudi Arabia News", news.saudi_news),
        "3": ("Sports News", news.sports_news),
        "4": ("Technology News", news.technology_news),
        "5": ("Keyword Search", news.search_news),
    }

    refresh_screen()

    while True:
        print_menu()

        choice = Prompt.ask(
            "[bold cyan]Enter your choice[/]",
            choices=[key for key, _, _ in MENU],
            show_choices=False,
        )

        if choice == "8":
            console.print("\n[bold green]Thank you for using Daily News & Weather![/]\n")
            break

        if choice in news_actions:
            name, action = news_actions[choice]
            articles = action()
            if articles:
                news_sections[name] = articles

        elif choice == "6":
            result = weather.show_weather()
            if result is not None:
                weather_data = result

        elif choice == "7":
            if news_sections or weather_data:
                pdf.generate_report(news_sections, weather_data)
            else:
                console.print(
                    "[yellow]Please load some news or check the "
                    "weather before saving a report.[/]"
                )

        console.print()
        Prompt.ask("[dim]Press Enter to return to the menu[/]", default="", show_default=False)
        refresh_screen()


if __name__ == "__main__":
    main()