# يعرض القوائم والنصوص بشكل جميل

# Fantasy Forest main menu with Arabic and English support.
import questionary
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from ui.audio import play_intro
from game.engine import run_game
from game.save_system import load_game
from game.explorers import display_hall
from game.localization import Localization
from ui.effects import console


FOREST_GREEN = "#2F5249"
ANTIQUE_GOLD = "#C5A46D"
SOFT_GREEN = "#A3B18A"


def show_main_menu():
    play_intro()
    loc = Localization()

    while True:
        console.print()

        heading = Text()
        heading.append("🌲 ✦ ELDERGROVE ✦ 🌲", style=f"bold {ANTIQUE_GOLD}")

        subtitle = Text(
            loc.display_text("game_title"),
            style=ANTIQUE_GOLD,
        )

        tagline = Text(
            loc.display_text("tagline"),
            style=f"dim {SOFT_GREEN}",
        )

        console.print(
            Panel(
                Group(heading, subtitle, tagline),
                border_style=FOREST_GREEN,
                padding=(1, 3),
                expand=False,
            )
        )

        language_option = (
            "English"
            if loc.language == "ar"
            else loc.format_arabic("العربية")
        )

        options = [
            ("1", "🌿", loc.display_text("start_game")),
            ("2", "📖", loc.display_text("continue_game")),
            ("3", "🏆", loc.display_text("hall_of_explorers")),
            ("4", "🌐", language_option),
            ("5", "🚪", loc.display_text("exit")),
        ]

        menu = Text()

        for index, icon, label in options:
            menu.append(f"{index}. ", style=ANTIQUE_GOLD)
            menu.append(f"{icon} ")
            menu.append(f"{label}\n", style=SOFT_GREEN)

        console.print(
            Panel(
                menu,
                title=f"[{ANTIQUE_GOLD}]✦ MENU ✦[/{ANTIQUE_GOLD}]",
                border_style=FOREST_GREEN,
                padding=(1, 3),
                expand=False,
            )
        )

        


        choice = questionary.select(
            loc.display_text("select_option"),
            choices=[
                questionary.Choice(
                    title=f"{icon} {loc.format_arabic(label) if False else label}",
                    value=index

                 )
                  for index, icon, label in options
            ],
            pointer="❯",
             use_shortcuts=False,
            style=questionary.Style([
                ("pointer", "fg:#C5A46D bold"),
                ("highlighted", "fg:#A3B18A bold"),
                ("selected", "fg:#2F5249"),
                ("question", "fg:#C5A46D"),
             ]),
        ).ask()
        if choice is None:
            continue






        if choice == "1":
            run_game(language=loc.language)

        elif choice == "2":
            saved_state = load_game()

            if saved_state is not None:
                saved_language = saved_state.get(
                    "language", loc.language
                )
                run_game(saved_state, language=saved_language)

        elif choice == "3":
            display_hall(loc)

        elif choice == "4":
            loc.set_language(
                "en" if loc.language == "ar" else "ar"
            )

        elif choice == "5":
            message = (
                "شكرًا لخوض مغامرة إلدرغروف!"
                if loc.language == "ar"
                else "Thank you for exploring Eldergrove!"
            )
            console.print(
                Text(loc.format_arabic(message), style=SOFT_GREEN)
            )
            break

        else:
            message = (
                "خيار غير صحيح، حاول مجددًا."
                if loc.language == "ar"
                else "Invalid option. Please try again."
            )
            console.print(
                Text(loc.format_arabic(message), style="red")
            )