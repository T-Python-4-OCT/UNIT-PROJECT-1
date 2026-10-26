# ألوان الغابة والمؤثرات النصية
import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.theme import Theme

from game.localization import Localization


FOREST_GREEN = "#2F5249"
ANTIQUE_GOLD = "#C5A46D"
SOFT_GREEN = "#A3B18A"
WOOD_BROWN = "#987554"
MIST_GRAY = "#9AA5A0"
DANGER_RED = "#C76D6D"

WORD_DELAY = 0.20
SCENE_DELAY = 0.80


FOREST_THEME = Theme({
    "forest": f"bold {FOREST_GREEN}",
    "gold": f"bold {ANTIQUE_GOLD}",
    "wood": WOOD_BROWN,
    "mystery": f"italic {SOFT_GREEN}",
    "danger": DANGER_RED,
    "success": SOFT_GREEN,
    "muted": MIST_GRAY,
})

console = Console(theme=FOREST_THEME)


def format_message(message, language="ar"):
    return Localization(language).format_arabic(str(message))


def show_panel(title, description="", style="forest"):
    content = description if description else title

    console.print(
        Panel(
            Text(str(content)),
            title=str(title),
            border_style=style,
            padding=(1, 2),
            expand=False,
        )
    )


def show_success(message):
    console.print(
        Text(f"✨ {message}", style="success")
    )


def show_error(message):
    console.print(
        Text(f"✖ {message}", style="danger")
    )


def show_separator():
    console.print(
        Rule(style=WOOD_BROWN)
    )


def show_forest_entry(language="ar"):
    message = (
        "🌲 تستيقظ الغابة القديمة..."
        if language == "ar"
        else "🌲 The ancient forest is awakening..."
    )

    with console.status(
        Text(
            format_message(message, language),
            style=SOFT_GREEN,
        ),
        spinner="dots",
        spinner_style=ANTIQUE_GOLD,
    ):
        time.sleep(5)

    console.print(
        Rule("✦ ELDERGROVE ✦", style=FOREST_GREEN)
    )


def show_magic_loading(language="ar"):
    message = (
        "🔮 تتوهج الرموز السحرية..."
        if language == "ar"
        else "🔮 Ancient runes are glowing..."
    )

    with console.status(
        Text(
            format_message(message, language),
            style=ANTIQUE_GOLD,
        ),
        spinner="moon",
        spinner_style=SOFT_GREEN,
    ):
        time.sleep(5)


def show_secret_discovery(language="ar", points=50):
    message = (
        "لقد اكتشفت أحد أسرار الغابة!"
        if language == "ar"
        else "You discovered a forest secret!"
    )

    points_message = (
        f"+{points} نقطة للأسرار"
        if language == "ar"
        else f"+{points} Secret Points"
    )

    content = Text(justify="center")
    content.append("✨ ")
    content.append(format_message(message, language))
    content.append("\n\n")
    content.append("✦ ")
    content.append(format_message(points_message, language))
    content.append(" ✦")

    console.print(
        Panel(
            content,
            title="🌿 ✦ SECRET DISCOVERED ✦ 🌿",
            border_style=ANTIQUE_GOLD,
            padding=(1, 2),
            expand=False,
        )
    )


def type_narration(
    text,
    delay=WORD_DELAY,
    style=SOFT_GREEN,
    formatter=None,
):
    words = str(text).split()

    if not words:
        console.print()
        return

    console.print()

    with Live(
        Text("", style=style),
        console=console,
        refresh_per_second=20,
        transient=False,
    ) as live:
        for index in range(1, len(words) + 1):
            current_text = " ".join(words[:index])

            if formatter is not None:
                current_text = formatter(current_text)

            live.update(
                Text(current_text, style=style),
                refresh=True,
            )

            time.sleep(delay)

    console.print()
    time.sleep(SCENE_DELAY)


def show_final_fate(language="ar"):
    message = (
        "🪄 الغابة تحدد مصيرك..."
        if language == "ar"
        else "🪄 The forest is deciding your fate..."
    )

    with console.status(
        Text(
            format_message(message, language),
            style=ANTIQUE_GOLD,
        ),
        spinner="earth",
        spinner_style=SOFT_GREEN,
    ):
        time.sleep(5)

    console.print()

    console.print(
        Rule(
            "✦ THE FOREST REMEMBERS ✦",
            style=ANTIQUE_GOLD,
        )
    )