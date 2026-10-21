
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from quran.quran_reader import QuranReader
from tafsir.tafsir_reader import TafsirReader

from interface.arabic_ui import (
    show_header,
    show_menu,
    show_ayah,
    show_message,
)
from interface.arabic_text import ArabicText

from player.audio_player import AudioPlayer


BASE_DIR = Path(__file__).resolve().parents[1]

QURAN_FILE = BASE_DIR / "data" / "quran.json"
TAFSIR_FILE = BASE_DIR / "data" / "tafsir.json"


MENU_OPTIONS = [
    ("1", "قراءة القرآن"),
    ("2", "الآية التالية"),
    ("3", "الآية السابقة"),
    ("4", "الانتقال إلى آية"),
    ("5", "تكرار الآية"),
    ("6", "التفسير الميسّر"),
    ("7", "البحث في القرآن"),
    ("8", "مساعدة"),
    ("9", "استماع وتكرار الآية 3 مرات"),
    ("10", "استماع إلى السورة الحالية"),
    ("11", "إيقاف التلاوة"),
    ("0", "خروج"),
]


def show_current_ayah(console, quran, surah, ayah):
    item = quran.find(surah, ayah)

    if item is None:
        show_message(console, "لم يتم العثور على الآية.")
        return None

    show_ayah(console, item)
    return item


def show_tafsir(console, tafsir, surah, ayah):
    text = tafsir.get(surah, ayah)

    if text is None:
        show_message(console, "التفسير غير متوفر لهذه الآية.", "yellow")
        return

    console.print(
        Panel(
            Text(ArabicText(text), justify="right"),
            title=ArabicText(f"التفسير الميسّر — {surah}:{ayah}"),
            border_style="green",
            padding=(1, 2),
        )
    )


def search_ayahs(console, quran):
    query = console.input(
        f"[bold cyan]{ArabicText('اكتب كلمة أو عبارة للبحث: ')}[/]"
    ).strip()

    results = quran.search(query)

    if not results:
        show_message(console, "لم يتم العثور على نتائج.")
        return

    console.print(
        f"\n[bold green]{ArabicText('عدد النتائج')}: {len(results)}[/]\n"
    )

    for item in results[:50]:
        console.print(
            Panel(
                Text(ArabicText(item["text"]), justify="right"),
                title=ArabicText(
                    f"{item['surah_name']} — السورة "
                    f"{item['surah_number']}، الآية "
                    f"{item['ayah_number']}"
                ),
                border_style="blue",
            )
        )

    if len(results) > 50:
        show_message(console, "تم عرض أول 50 نتيجة فقط.", "yellow")


def show_help(console):
    help_text = (
        "1. قراءة آية\n"
        "2. الانتقال إلى الآية التالية\n"
        "3. الرجوع إلى الآية السابقة\n"
        "4. الانتقال إلى سورة وآية محددتين\n"
        "5. إعادة عرض الآية الحالية\n"
        "6. عرض التفسير الميسّر\n"
        "7. البحث في نص القرآن\n"
        "8. عرض المساعدة\n"
        "9. تشغيل الآية الحالية 3 مرات\n"
        "10. تشغيل السورة الحالية\n"
        "11. إيقاف التلاوة\n"
        "0. الخروج من البرنامج"
    )

    console.print(
        Panel(
            ArabicText(help_text),
            title=ArabicText("المساعدة"),
            border_style="cyan",
        )
    )


def run_cli():
    console = Console()

    try:
        quran = QuranReader(QURAN_FILE)
        tafsir = TafsirReader(TAFSIR_FILE)
    except (OSError, ValueError) as error:
        show_message(
            console,
            f"تعذّر تحميل البيانات: {error}",
            "red",
        )
        return

    if not quran.ayahs:
        show_message(console, "ملف القرآن لا يحتوي على آيات.", "red")
        return

    try:
        player = AudioPlayer()
    except Exception as error:
        show_message(
            console,
            f"تعذّر تهيئة مشغل الصوت: {error}",
            "red",
        )
        return

    current_surah = 1
    current_ayah = 1

    try:
        show_header(console)

        console.print(
            f"[green]{ArabicText('تم تحميل')} "
            f"{quran.get_ayah_count()} "
            f"{ArabicText('آية.')}[/]"
        )

        console.print(
            f"[green]{ArabicText('عدد التفسيرات المحمّلة:')} "
            f"{tafsir.get_count()}[/]"
        )

        show_current_ayah(
            console,
            quran,
            current_surah,
            current_ayah,
        )

        while True:
            show_menu(console, MENU_OPTIONS)

            choice = console.input(
                f"\n[bold cyan]{ArabicText(' اختر رقم العملية: ')}[/]"
            ).strip()

            if choice == "0":
                show_message(console, "شكرًا لاستخدام تيسير.")
                break

            elif choice == "1":
                show_current_ayah(
                    console, quran, current_surah, current_ayah
                )

            elif choice == "2":
                if quran.find(current_surah, current_ayah + 1):
                    current_ayah += 1
                else:
                    next_surah = current_surah + 1

                    while next_surah <= 114:
                        if quran.find(next_surah, 1):
                            current_surah = next_surah
                            current_ayah = 1
                            break

                        next_surah += 1
                    else:
                        show_message(
                            console,
                            "وصلت إلى نهاية القرآن الكريم.",
                        )
                        continue

                show_current_ayah(
                    console, quran, current_surah, current_ayah
                )

            elif choice == "3":
                if current_ayah > 1:
                    current_ayah -= 1

                elif current_surah > 1:
                    current_surah -= 1
                    previous_surah = quran.get_surah(current_surah)

                    while not previous_surah and current_surah > 1:
                        current_surah -= 1
                        previous_surah = quran.get_surah(current_surah)

                    if previous_surah:
                        current_ayah = previous_surah[-1]["ayah_number"]
                else:
                    show_message(
                        console,
                        "أنت في بداية القرآن الكريم.",
                        "yellow",
                    )
                    continue

                show_current_ayah(
                    console, quran, current_surah, current_ayah
                )

            elif choice == "4":
                try:
                    surah = int(
                        console.input(
                            ArabicText("أدخل رقم السورة: ")
                        ).strip()
                    )
                    ayah = int(
                        console.input(
                            ArabicText("أدخل رقم الآية: ")
                        ).strip()
                    )
                except ValueError:
                    show_message(
                        console, "أدخل أرقامًا صحيحة.", "red"
                    )
                    continue

                item = quran.find(surah, ayah)

                if item is None:
                    show_message(
                        console,
                        "السورة أو الآية غير موجودة.",
                        "yellow",
                    )
                    continue

                current_surah = surah
                current_ayah = ayah
                show_ayah(console, item)

            elif choice == "5":
                show_current_ayah(
                    console, quran, current_surah, current_ayah
                )

            elif choice == "6":
                show_tafsir(
                    console, tafsir, current_surah, current_ayah
                )

            elif choice == "7":
                search_ayahs(console, quran)

            elif choice == "8":
                show_help(console)

            elif choice == "9":
                player.play_ayah(
                    current_surah,
                    current_ayah,
                    repeats=3,
                )

            elif choice == "10":
                ayahs = quran.get_surah(current_surah)
                player.play_surah(ayahs)

            elif choice == "11":
                player.stop()

            else:
                show_message(
                    console,
                    "اختيار غير صحيح. حاول مرة أخرى.",
                    "yellow",
                )

    except KeyboardInterrupt:
        show_message(console, "تم إيقاف البرنامج.")

    finally:
        player.close()


if __name__ == "__main__":
    run_cli()
