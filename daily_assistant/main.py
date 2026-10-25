
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

from news import NewsManager
from weather import show_weather
from pdf_report import PDFReport
from ui import banner, console


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
        Panel(
            table,
            title="[bold]MAIN MENU[/]",
            border_style="cyan",
            expand=False,
            padding=(1, 3),
        )
    )


def main():
    news_manager = NewsManager()
    news_sections = {}
    weather_data = None
    pdf_report = PDFReport()

    NEWS_ACTIONS = {
        "1": ("World News", news_manager.show_top_news),
        "2": ("Saudi Arabia News", news_manager.show_saudi_news),
        "3": ("Sports News", news_manager.show_sports_news),
        "4": ("Technology News", news_manager.show_technology_news),
        "5": ("Keyword Search", news_manager.search_news),
    }

    console.clear()
    banner()

    while True:
        print_menu()

        choice = Prompt.ask(
            "[bold cyan]Enter your choice[/]",
            choices=[item[0] for item in MENU],
            show_choices=False,
        )

        if choice == "8":
            console.print(
                "\n[bold green]Thank you for using "
                "Daily News & Weather![/]\n"
            )
            break

        if choice in NEWS_ACTIONS:
            category, action = NEWS_ACTIONS[choice]
            articles = action()

            if articles:
                news_sections[category] = articles

        elif choice == "6":
            result = show_weather()

            if result is not None:
                weather_data = result

        elif choice == "7":
            if not news_sections and weather_data is None:
                console.print(
                    "[yellow]Please load some news or check the "
                    "weather before saving a report.[/]"
                )
            else:
                pdf_path = pdf_report.generate_report(
                    news_sections,
                    weather_data,
                )

                if pdf_path:
                    console.print(
                        "[bold green]Your PDF report is ready![/]"
                    )

        console.print()

        Prompt.ask(
            "[dim]Press Enter to return to the menu[/]",
            default="",
            show_default=False,
        )

        console.clear()
        banner()


if __name__ == "__main__":
    main()
