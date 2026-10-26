from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ai_summary import summarize_news
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
        Panel(
            table,
            title="[bold]MAIN MENU[/]",
            border_style="cyan",
            expand=False,
            padding=(1, 3),
        )
    )


def refresh_screen():
    console.clear()
    banner()


def get_menu_choice():
    valid_choices = [key for key, _, _ in MENU]

    while True:
        choice = console.input(
            "[bold cyan]Enter your choice:[/] "
        ).strip()

        if not choice:
            console.print(
                "[bold red]Input cannot be empty![/]"
            )
        elif not choice.isdigit():
            console.print(
                "[bold red]Invalid input! Please enter a number only.[/]"
            )
        elif choice not in valid_choices:
            console.print(
                "[bold red]Wrong number! Please choose a number from the menu.[/]"
            )
        else:
            return choice


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
        choice = get_menu_choice()

        if choice == "8":
            console.print(
                "\n[bold green]Thank you for using Daily News & Weather![/]\n"
            )
            break

        elif choice in news_actions:
            name, action = news_actions[choice]

            try:
                articles = action()

                if articles:
                    news_sections[name] = articles
                else:
                    console.print(
                        "[yellow]No articles were returned.[/]"
                    )

            except Exception as err:
                console.print(
                    f"[bold red]Unable to retrieve news: {err}[/]"
                )

        elif choice == "6":
            try:
                result = weather.show_weather()

                if result is not None:
                    weather_data = result

            except Exception as err:
                console.print(
                    f"[bold red]Unable to retrieve weather: {err}[/]"
                )

        elif choice == "7":
            ai_summary = None

            if news_sections:
                console.print(
                    "[bold cyan]Generating English and Arabic summaries...[/]"
                )
                ai_summary = summarize_news(news_sections)

                if ai_summary:
                    console.print(
                        "[green]Summary generated successfully.[/]"
                    )
                else:
                    console.print(
                        "[yellow]Summary unavailable. Check the AI error above.[/]"
                    )
            else:
                console.print(
                    "[yellow]No news collected yet. Select a news option first.[/]"
                )

            try:
                output_path = pdf.generate_report(
                    news_sections,
                    weather_data,
                    ai_summary,
                )

                if output_path:
                    console.print(
                        Panel(
                            f"PDF created successfully!\n{output_path}",
                            title="PDF Report",
                            border_style="green",
                        )
                    )
                else:
                    console.print(
                        "[bold red]PDF creation failed. Check the error above.[/]"
                    )

            except Exception as err:
                console.print(
                    f"[bold red]PDF creation failed: {err}[/]"
                )

        console.print()
        Prompt.ask(
            "[dim]Press Enter to return to the menu[/]",
            default="",
            show_default=False,
        )
        refresh_screen()


if __name__ == "__main__":
    main()