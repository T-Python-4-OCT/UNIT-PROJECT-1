
from rich.align import Align
from rich.box import ROUNDED, HEAVY
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from interface.arabic_text import ArabicText


# ألوان تصميم تيسير
GOLD = "#D9BD7C"
GOLD_LIGHT = "#E8D29B"
EMERALD = "#176B50"
EMERALD_LIGHT = "#D7E6DD"
MUTED = "#A8BFB4"
WHITE = "#F5F5F0"


def _arabic(value) -> str:
    """تهيئة النص العربي للعرض في الطرفية."""
    return str(ArabicText(str(value)))


def show_header(console: Console):
    """عرض عنوان التطبيق."""

    title = Text(
        _arabic("۞ تيسير ۞"),
        style=f"bold {GOLD_LIGHT}",
    )
    title.justify = "center"

    subtitle = Text(
        _arabic("المصحف الصوتي والتدبّر"),
        style=f"bold {EMERALD_LIGHT}",
    )
    subtitle.justify = "center"

    slogan = Text(
        _arabic("اقرأ • استمع • كرّر • تدبّر"),
        style=f"italic {MUTED}",
    )
    slogan.justify = "center"

    content = Group(
        Align.center(title),
        Align.center(subtitle),
        Align.center(slogan),
    )

    console.print()

    console.print(
        Panel(
            content,
            title=Text("T A Y S I R", style=f"bold {GOLD}"),
            title_align="center",
            border_style=GOLD,
            box=HEAVY,
            padding=(1, 2),
            expand=True,
        )
    )


def _get_menu_sections(options):
    """تقسيم الخيارات إلى أقسام."""

    sections = {
        "القرآن الكريم": [],
        "التلاوة والاستماع": [],
        "المساعد الذكي": [],
        "عام": [],
    }

    for number, option in options:
        label = str(option)
        normalized = label.lower()

        if any(
            word in normalized
            for word in ("خروج", "مساعدة", "help")
        ):
            sections["عام"].append((str(number), label))

        elif any(
            word in normalized
            for word in (
                "وكيل",
                "ذكاء",
                "محادثة",
                "agent",
                "ai",
            )
        ):
            sections["المساعد الذكي"].append(
                (str(number), label)
            )

        elif any(
            word in normalized
            for word in (
                "استماع",
                "تلاوة",
                "إيقاف",
                "ايقاف",
                "تشغيل",
                "صوت",
                "تكرار",
            )
        ):
            sections["التلاوة والاستماع"].append(
                (str(number), label)
            )

        else:
            sections["القرآن الكريم"].append(
                (str(number), label)
            )

    return [
        (title, items)
        for title, items in sections.items()
        if items
    ]


def show_menu(console: Console, options=None):
    """عرض القائمة الرئيسية بإطارات خضراء دون تعبئة الخلفية."""

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

    sections = _get_menu_sections(options)
    cards = []

    for section_title, items in sections:
        table = Table.grid(
            expand=True,
            padding=(0, 1),
        )

        table.add_column(
            "number",
            width=5,
            justify="center",
            no_wrap=True,
        )

        table.add_column(
            "option",
            ratio=1,
        )

        for number, label in items:
            number_text = Text(
                number,
                style=f"bold {GOLD_LIGHT}",
            )

            label_text = Text(
                _arabic(label),
                style=WHITE,
            )
            label_text.justify = "right"

            table.add_row(
                number_text,
                Align.right(label_text),
            )

        # إطار أخضر فقط، بدون لون خلفية.
        card = Panel(
            table,
            title=Text(
                _arabic(section_title),
                style=f"bold {GOLD_LIGHT}",
            ),
            title_align="right",
            border_style=EMERALD,
            box=ROUNDED,
            padding=(1, 1),
            expand=True,
        )

        cards.append(card)

    layout = Table.grid(
        expand=True,
        padding=(0, 1),
    )
    layout.add_column(ratio=1)

    for card in cards:
        layout.add_row(card)

    console.print()

    # الإطار الخارجي ذهبي، دون تعبئة خلفية.
    console.print(
        Panel(
            layout,
            title=Text(
                _arabic("القائمة الرئيسية"),
                style=f"bold {EMERALD_LIGHT}",
            ),
            title_align="right",
            border_style=GOLD,
            box=ROUNDED,
            padding=(1, 1),
            expand=True,
        )
    )

    console.print(
        Align.center(
            Text(
                _arabic("أدخل رقم الخيار للمتابعة"),
                style=f"italic {MUTED}",
            )
        )
    )

    console.print()


def _normalize_digits(value: str) -> str:
    """تحويل الأرقام العربية والفارسية إلى أرقام إنجليزية."""

    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"

    translation = {}

    for index, digit in enumerate(arabic_digits):
        translation[ord(digit)] = str(index)

    for index, digit in enumerate(persian_digits):
        translation[ord(digit)] = str(index)

    return value.translate(translation)


def ask_number(
    console: Console,
    prompt: str,
    minimum: int,
    maximum: int,
):
    """طلب رقم من المستخدم والتحقق من صحته."""

    while True:
        raw = console.input(
            _arabic(prompt)
        ).strip()

        raw = _normalize_digits(raw)

        try:
            value = int(raw)

            if minimum <= value <= maximum:
                return value

        except ValueError:
            pass

        show_message(
            console,
            f"أدخل رقمًا صحيحًا من {minimum} إلى {maximum}.",
            style="bold red",
        )


def show_ayah(console: Console, ayah: dict):
    """عرض الآية داخل إطار ذهبي."""

    surah_name = ayah.get(
        "surah_name",
        ayah.get("sura_name_ar", "القرآن الكريم"),
    )

    ayah_number = ayah.get(
        "ayah_number",
        ayah.get("aya_no", ""),
    )

    ayah_text = ayah.get(
        "text",
        ayah.get("aya_text", ""),
    )

    heading = f"{surah_name} — الآية {ayah_number}"

    verse = Text(
        _arabic(ayah_text),
        style=f"bold {WHITE}",
    )
    verse.justify = "right"

    console.print()

    console.print(
        Panel(
            Align.right(verse),
            title=Text(
                _arabic(heading),
                style=f"bold {GOLD_LIGHT}",
            ),
            title_align="right",
            subtitle=Text(
                _arabic("تيسير • تلاوة وتدبّر"),
                style=f"italic {MUTED}",
            ),
            subtitle_align="center",
            border_style=GOLD,
            box=ROUNDED,
            padding=(2, 2),
            expand=True,
        )
    )


def show_message(
    console: Console,
    message,
    style="green",
):
    """عرض رسالة دون إضافة خلفية ملونة."""

    message_text = Text(
        _arabic(message),
        style=style,
    )
    message_text.justify = "right"

    console.print(
        Align.right(message_text)
    )


def show_section(
    console: Console,
    title,
    message="",
):
    """عرض قسم بإطار أخضر دون تعبئة الخلفية."""

    content = Text(
        _arabic(message),
        style=WHITE,
    )
    content.justify = "right"

    console.print(
        Panel(
            Align.right(content),
            title=Text(
                _arabic(title),
                style=f"bold {GOLD_LIGHT}",
            ),
            title_align="right",
            border_style=EMERALD,
            box=ROUNDED,
            padding=(1, 2),
            expand=True,
        )
    )
