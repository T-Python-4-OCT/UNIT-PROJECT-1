from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from interface.arabic_text import ArabicText


def show_header(console: Console):
    title = Text(
        str(ArabicText("۞ تيسير ۞")),
        style="bold #E8D29B",
        justify="center",
    )

    subtitle = Text(
        str(ArabicText("المصحف الصوتي والتدبّر")),
        style="#D7E6DD",
        justify="center",
    )

    slogan = Text(
        str(ArabicText("اقرأ • استمع • كرّر • تدبّر")),
        style="italic #B6C9BF",
        justify="center",
    )

    body = Text()
    body.append_text(title)
    body.append("\n")
    body.append_text(subtitle)
    body.append("\n")
    body.append_text(slogan)

    console.print(
        Panel(
            Align.center(body),
            border_style="#D9BD7C",
            padding=(1, 2),
        )
    )


def show_menu(console: Console, options=None):
    if options is None:
        options = [
            ("1", "قراءة القرآن"),
            ("2", "الآية التالية"),
            ("3", "الآية السابقة"),
            ("4", "الانتقال إلى آية"),
            ("5", "تكرار الآية"),
            ("6", "التفسير الميسّر"),
            ("7", "البحث في القرآن"),
            ("8", "مساعدة"),
            ("0", "خروج"),
        ]

    console.print()

    for number, option in options:
        menu_text = Text(
            f"{number}. {ArabicText(option)}",
            justify="right",
        )
        console.print(Align.right(menu_text))

    console.print()


def ask_number(
    console: Console,
    prompt: str,
    minimum: int,
    maximum: int,
):
    while True:
        raw = console.input(str(ArabicText(prompt))).strip()

        try:
            value = int(raw)

            if minimum <= value <= maximum:
                return value

        except ValueError:
            pass

        error_message = f"أدخل رقمًا من {minimum} إلى {maximum}."

        console.print(
            Align.right(
                Text(
                    str(ArabicText(error_message)),
                    style="red",
                )
            )
        )


def show_ayah(console: Console, ayah: dict):
    title = str(
        ArabicText(
            f"{ayah['surah_name']} — الآية {ayah['ayah_number']}"
        )
    )

    text = str(ArabicText(ayah["text"]))

    console.print(
        Panel(
            Align.right(Text(text, justify="right")),
            title=title,
            border_style="#D9BD7C",
            padding=(1, 2),
        )
    )


def show_message(
    console: Console,
    message: str,
    style: str = "green",
):
    console.print(
        Align.right(
            Text(
                str(ArabicText(message)),
                style=style,
                justify="right",
            )
        )
    )
