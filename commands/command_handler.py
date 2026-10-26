
from pathlib import Path
from types import SimpleNamespace
import re

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
from commands.intent_parser import IntentParser
from voice.voice_agent import VoiceAgent
from voice.najdi_tts import NajdiTTS
from ai_agent import TaysirAIAgent


BASE_DIR = Path(__file__).resolve().parents[1]
QURAN_FILE = BASE_DIR / "data" / "quran.json"
TAFSIR_FILE = BASE_DIR / "data" / "tafsir.json"


MENU_OPTIONS = [
    ("1", "قراءة الآية الحالية"),
    ("2", "الآية التالية"),
    ("3", "الآية السابقة"),
    ("4", "الانتقال إلى آية"),
    ("5", "تكرار الآية بعدد تحدده"),
    ("6", "التفسير الميسّر"),
    ("7", "البحث في القرآن"),
    ("8", "مساعدة"),
    ("9", "استماع وتكرار الآية 3 مرات"),
    ("10", "استماع إلى السورة الحالية"),
    ("11", "إيقاف التلاوة"),
    ("12", "الوكيل الذكي — كتابة وصوت"),
    ("0", "خروج"),
]


def normalize_digits(value):
    translation = str.maketrans(
        "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
        "01234567890123456789",
    )
    return str(value).translate(translation)


def normalize_arabic(value):
    value = normalize_digits(str(value or "").strip())

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    value = value.replace("تسفير", "تفسير")
    value = re.sub(r"[\u064B-\u065F\u0670ـ]", "", value)
    value = re.sub(r"[؟?!،,.:؛;]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def build_surah_names(quran):
    names = {}
    for item in quran.ayahs:
        names.setdefault(item["surah_number"], item["surah_name"])
    return names


def find_surah_in_command(command, quran):
    normalized = normalize_arabic(command)

    for number, name in build_surah_names(quran).items():
        normalized_name = normalize_arabic(name)
        if normalized_name and normalized_name in normalized:
            return number

    match = re.search(r"(?:السوره|سوره)\s*(?:رقم\s*)?(\d+)", normalized)
    if match:
        number = int(normalize_digits(match.group(1)))
        if 1 <= number <= 114:
            return number

    return None


def find_ayah_number(command):
    normalized = normalize_arabic(command)
    match = re.search(r"(?:الاية|الايه|ايه)\s*(?:رقم\s*)?(\d+)", normalized)
    if match:
        return int(normalize_digits(match.group(1)))
    return None


def command_requests_audio(command):
    normalized = normalize_arabic(command)

    audio_verbs = (
        "اقرا",
        "قراءه",
        "تلاوه",
        "شغل",
        "اسمع",
        "استمع",
        "ابغى اسمع",
        "ابي اسمع",
        "اريد سماع",
    )
    return any(verb in normalized for verb in audio_verbs)


def command_requests_full_surah(command):
    normalized = normalize_arabic(command)

    mentions_surah = "سوره" in normalized
    audio_verbs = (
        "اقرا",
        "قراءه",
        "تلاوه",
        "شغل",
        "اسمع",
        "استمع",
    )
    asks_full = any(
        phrase in normalized
        for phrase in (
            "كامله",
            "كامل",
            "بالكامل",
            "السوره كلها",
        )
    )

    return mentions_surah and (
        asks_full or any(verb in normalized for verb in audio_verbs)
    )


def command_requests_next_surah(command):
    normalized = normalize_arabic(command)

    phrases = (
        "السوره التاليه",
        "السوره اللي بعدها",
        "السوره التي بعدها",
        "السوره الجايه",
        "السوره القادمه",
    )
    return any(phrase in normalized for phrase in phrases)


def show_current_ayah(console, quran, surah, ayah):
    item = quran.find(surah, ayah)

    if item is None:
        show_message(console, "لم يتم العثور على الآية.", "yellow")
        return None

    show_ayah(console, item)
    return item


def show_tafsir(console, tafsir, surah, ayah):
    text = tafsir.get(surah, ayah)

    if not text:
        show_message(
            console,
            "التفسير غير متوفر لهذه الآية.",
            "yellow",
        )
        return

    console.print(
        Panel(
            Text(ArabicText(text), justify="right"),
            title=ArabicText(f"التفسير الميسّر — {surah}:{ayah}"),
            border_style="green",
            padding=(1, 2),
        )
    )


def show_surah_tafsir(console, quran, tafsir, surah):
    ayahs = quran.get_surah(surah)

    if not ayahs:
        show_message(console, "لم يتم العثور على السورة.", "yellow")
        return

    surah_name = ayahs[0].get("surah_name", f"السورة {surah}")

    for item in ayahs:
        ayah_number = item["ayah_number"]
        tafsir_text = tafsir.get(surah, ayah_number)

        if not tafsir_text:
            tafsir_text = "التفسير غير متوفر لهذه الآية."

        content = (
            f"الآية:\n{item['text']}\n\n"
            f"التفسير الميسّر:\n{tafsir_text}"
        )

        console.print(
            Panel(
                Text(ArabicText(content), justify="right"),
                title=ArabicText(f"{surah_name} — الآية {ayah_number}"),
                border_style="blue",
                padding=(1, 2),
            )
        )


def search_ayahs(console, quran, query=None):
    if query is None:
        query = console.input(
            f"[bold cyan]{ArabicText('اكتب كلمة أو عبارة للبحث: ')}[/]"
        ).strip()

    if not query:
        show_message(console, "اكتب كلمة أو عبارة للبحث.", "yellow")
        return

    results = quran.search(query)

    if not results:
        show_message(console, "لم يتم العثور على نتائج.", "yellow")
        return

    console.print(
        f"\n[bold green]{ArabicText('عدد النتائج')}: {len(results)}[/]\n"
    )

    for item in results[:50]:
        console.print(
            Panel(
                Text(ArabicText(item["text"]), justify="right"),
                title=ArabicText(
                    f'{item["surah_name"]} — السورة '
                    f'{item["surah_number"]}، الآية {item["ayah_number"]}'
                ),
                border_style="blue",
            )
        )

    if len(results) > 50:
        show_message(console, "تم عرض أول 50 نتيجة فقط.", "yellow")


def show_help(console):
    help_text = (
        "1. قراءة الآية الحالية\n"
        "2. الانتقال إلى الآية التالية\n"
        "3. الرجوع إلى الآية السابقة\n"
        "4. الانتقال إلى سورة وآية محددتين\n"
        "5. تكرار الآية بعدد تحدده\n"
        "6. عرض التفسير الميسّر\n"
        "7. البحث في القرآن\n"
        "8. عرض المساعدة\n"
        "9. تشغيل الآية الحالية 3 مرات\n"
        "10. تشغيل السورة الحالية\n"
        "11. إيقاف التلاوة\n"
        "12. الوكيل الذكي: كتابة وصوت\n"
        "0. الخروج"
    )

    console.print(
        Panel(
            ArabicText(help_text),
            title=ArabicText("المساعدة"),
            border_style="cyan",
        )
    )


def build_quran_context(quran, tafsir, current_surah, current_ayah):
    item = quran.find(current_surah, current_ayah) or {}

    return {
        "current_ayah": {
            "surah": current_surah,
            "ayah": current_ayah,
            "text": item.get("text", ""),
        },
        "current_tafsir": tafsir.get(current_surah, current_ayah) or "",
    }


def is_current_tafsir_request(command):
    normalized = normalize_arabic(command)

    asks_tafsir = any(
        word in normalized
        for word in ("تفسير", "فسر", "اشرح", "معنى الايه")
    )
    asks_current = any(
        word in normalized
        for word in ("الحاليه", "الحالي", "هذه الايه", "هذي الايه")
    )

    return asks_tafsir and asks_current


def is_surah_tafsir_request(command):
    normalized = normalize_arabic(command)
    asks_tafsir = any(
        word in normalized
        for word in ("تفسير", "فسر", "اشرح", "التفسير", "معنى")
    )
    return asks_tafsir and "سوره" in normalized


def play_requested_surah(console, quran, player, command, current_surah):
    """تشغيل السورة المذكورة في الأمر، أو السورة الحالية إذا لم تُذكر."""
    target_surah = find_surah_in_command(command, quran)
    if target_surah is None:
        target_surah = current_surah

    ayahs = quran.get_surah(target_surah)
    if not ayahs:
        show_message(console, "لم يتم العثور على السورة المطلوبة.", "yellow")
        return current_surah, False

    player.play_surah(ayahs)
    show_message(
        console,
        f"بدأ تشغيل سورة {ayahs[0].get('surah_name', target_surah)}.",
    )
    return target_surah, True


def ask_repeat_count(console):
    """طلب عدد تكرارات صالح من المستخدم."""
    while True:
        raw_value = console.input(
            f"[bold cyan]{ArabicText('كم مرة تريد تكرار الآية؟ ')}[/]"
        ).strip()

        try:
            count = int(normalize_digits(raw_value))
        except ValueError:
            show_message(console, "أدخل عددًا صحيحًا، مثل 5.", "yellow")
            continue

        if count < 1:
            show_message(console, "عدد التكرارات يجب أن يكون 1 أو أكثر.", "yellow")
            continue

        if count > 100:
            show_message(console, "الحد الأعلى للتكرار هو 100 مرة.", "yellow")
            continue

        return count


def handle_smart_command(
    console,
    parser,
    quran,
    tafsir,
    player,
    current_surah,
    current_ayah,
    command=None,
    intent_override=None,
    voice_agent=None,
):
    """تنفيذ الأوامر المحلية مع الفصل بين عرض النص وتشغيل الصوت."""
    if command is None:
        command = console.input(
            f"\n[bold cyan]{ArabicText('اكتب أمرك لتيسير: ')}[/]"
        ).strip()

    if not command or not command.strip():
        show_message(console, "لم يتم إدخال أي أمر.", "yellow")
        return current_surah, current_ayah

    intent = (
        intent_override
        if intent_override is not None
        else parser.parse(command)
    )

    action = getattr(intent, "action", "unknown")
    target_surah = getattr(intent, "surah", None)
    target_ayah = getattr(intent, "ayah", None)
    play_audio = bool(getattr(intent, "play_audio", False))
    repeats = getattr(intent, "repeats", 1)

    try:
        repeats = max(1, min(100, int(repeats)))
    except (TypeError, ValueError):
        repeats = 1

    def valid_location(surah, ayah=None):
        if surah is None:
            return False
        try:
            surah = int(surah)
        except (TypeError, ValueError):
            return False
        if not 1 <= surah <= 114:
            return False
        if ayah is None:
            return bool(quran.get_surah(surah))
        try:
            ayah = int(ayah)
        except (TypeError, ValueError):
            return False
        return quran.find(surah, ayah) is not None

    def display_surah(surah):
        ayahs = quran.get_surah(surah)
        if not ayahs:
            show_message(console, "لم يتم العثور على السورة.", "yellow")
            return False

        name = ayahs[0].get("surah_name", f"السورة {surah}")
        console.print(
            Panel(
                Text(
                    ArabicText(
                        f"{name} — عدد الآيات: {len(ayahs)}"
                    ),
                    justify="right",
                ),
                title=ArabicText("عرض السورة"),
                border_style="green",
            )
        )
        for item in ayahs:
            show_ayah(console, item)
        return True

    if action == "unknown":
        show_message(
            console,
            "لم أفهم الأمر. جرّب: اعرض الآية 3 من سورة الناس، "
            "اقرأ الآية 3 من سورة الناس، تفسير سورة البقرة، "
            "أو ابحث عن الحمد لله.",
            "yellow",
        )
        return current_surah, current_ayah

    if action in ("read", "show_ayah", "display_ayah"):
        if target_surah is not None or target_ayah is not None:
            if target_surah is None:
                target_surah = current_surah
            if target_ayah is None:
                target_ayah = current_ayah

            if not valid_location(target_surah, target_ayah):
                show_message(console, "السورة أو الآية غير موجودة.", "yellow")
                return current_surah, current_ayah

            current_surah, current_ayah = int(target_surah), int(target_ayah)

        show_current_ayah(console, quran, current_surah, current_ayah)
        if play_audio:
            player.play_ayah(
                current_surah, current_ayah, repeats=repeats
            )
        return current_surah, current_ayah

    if action in ("show_surah", "display_surah"):
        if target_surah is None:
            target_surah = find_surah_in_command(command, quran)
        if not valid_location(target_surah):
            show_message(
                console,
                "حدّد السورة التي تريد عرضها، مثل: اعرض سورة الناس.",
                "yellow",
            )
            return current_surah, current_ayah

        target_surah = int(target_surah)
        if display_surah(target_surah):
            current_surah, current_ayah = target_surah, 1
        if play_audio:
            player.play_surah(quran.get_surah(current_surah))
        return current_surah, current_ayah

    if action == "goto":
        if target_surah is None:
            target_surah = current_surah
        if target_ayah is None:
            show_message(
                console,
                "حدّد رقم الآية، مثل: انتقل إلى الآية 3 من سورة الناس.",
                "yellow",
            )
            return current_surah, current_ayah

        if not valid_location(target_surah, target_ayah):
            show_message(console, "السورة أو الآية غير موجودة.", "yellow")
            return current_surah, current_ayah

        current_surah, current_ayah = int(target_surah), int(target_ayah)
        show_current_ayah(console, quran, current_surah, current_ayah)

        if play_audio:
            player.play_ayah(
                current_surah, current_ayah, repeats=repeats
            )
        return current_surah, current_ayah

    if action == "next":
        if quran.find(current_surah, current_ayah + 1):
            current_ayah += 1
        else:
            next_surah = current_surah + 1
            while next_surah <= 114 and not quran.find(next_surah, 1):
                next_surah += 1
            if next_surah > 114:
                show_message(console, "وصلت إلى نهاية القرآن الكريم.")
                return current_surah, current_ayah
            current_surah, current_ayah = next_surah, 1

        show_current_ayah(console, quran, current_surah, current_ayah)
        if play_audio:
            player.play_ayah(
                current_surah, current_ayah, repeats=repeats
            )
        return current_surah, current_ayah

    if action == "previous":
        if current_ayah > 1:
            current_ayah -= 1
        elif current_surah > 1:
            previous_surah = current_surah - 1
            while previous_surah > 1 and not quran.get_surah(previous_surah):
                previous_surah -= 1
            previous_ayahs = quran.get_surah(previous_surah)
            if previous_ayahs:
                current_surah = previous_surah
                current_ayah = previous_ayahs[-1]["ayah_number"]
        else:
            show_message(console, "أنت في بداية القرآن الكريم.", "yellow")
            return current_surah, current_ayah

        show_current_ayah(console, quran, current_surah, current_ayah)
        if play_audio:
            player.play_ayah(
                current_surah, current_ayah, repeats=repeats
            )
        return current_surah, current_ayah

    if action in ("tafsir", "tafsir_ayah"):
        if target_surah is None:
            target_surah = current_surah
        if target_ayah is None:
            target_ayah = current_ayah
        if not valid_location(target_surah, target_ayah):
            show_message(console, "السورة أو الآية غير موجودة.", "yellow")
            return current_surah, current_ayah

        current_surah, current_ayah = int(target_surah), int(target_ayah)
        show_tafsir(console, tafsir, current_surah, current_ayah)
        return current_surah, current_ayah

    if action in ("tafsir_surah", "show_surah_tafsir"):
        if target_surah is None:
            target_surah = find_surah_in_command(command, quran)
        if not valid_location(target_surah):
            show_message(
                console,
                "حدّد السورة التي تريد تفسيرها، مثل: تفسير سورة البقرة.",
                "yellow",
            )
            return current_surah, current_ayah

        current_surah, current_ayah = int(target_surah), 1
        show_surah_tafsir(console, quran, tafsir, current_surah)
        return current_surah, current_ayah

    if action == "repeat":
        if play_audio:
            player.play_ayah(
                current_surah, current_ayah, repeats=repeats
            )
        else:
            show_current_ayah(console, quran, current_surah, current_ayah)
        return current_surah, current_ayah

    if action == "play_ayah":
        if target_surah is None:
            target_surah = current_surah
        if target_ayah is None:
            target_ayah = current_ayah
        if not valid_location(target_surah, target_ayah):
            show_message(console, "السورة أو الآية غير موجودة.", "yellow")
            return current_surah, current_ayah

        current_surah, current_ayah = int(target_surah), int(target_ayah)
        show_current_ayah(console, quran, current_surah, current_ayah)
        player.play_ayah(
            current_surah, current_ayah, repeats=repeats
        )
        return current_surah, current_ayah

    if action == "play_surah":
        if target_surah is None:
            target_surah = find_surah_in_command(command, quran)

        if not valid_location(target_surah):
            show_message(
                console,
                "حدّد السورة التي تريد الاستماع إليها، مثل: اقرأ سورة الفاتحة.",
                "yellow",
            )
            return current_surah, current_ayah

        current_surah, current_ayah = int(target_surah), 1
        player.play_surah(quran.get_surah(current_surah))
        show_message(
            console,
            f"بدأ تشغيل سورة {quran.get_surah(current_surah)[0].get('surah_name', current_surah)}.",
        )
        return current_surah, current_ayah

    if action == "search":
        search_ayahs(console, quran, getattr(intent, "query", None))
        return current_surah, current_ayah

    if action == "stop":
        player.stop()
        show_message(console, "تم طلب إيقاف التلاوة.")
        return current_surah, current_ayah

    if action == "help":
        show_help(console)
        return current_surah, current_ayah

    if action == "exit":
        show_message(
            console,
            "للخروج من البرنامج، اختر 0 من القائمة الرئيسية.",
            "yellow",
        )
        return current_surah, current_ayah

    show_message(console, "هذا الأمر غير مدعوم بعد.", "yellow")
    return current_surah, current_ayah

def run_ai_agent_chat(
    console,
    quran,
    tafsir,
    player,
    parser,
    current_surah,
    current_ayah,
    voice_agent=None,
):
    """وكيل واحد يدعم الكتابة والصوت والأوامر المحلية."""
    try:
        tts = NajdiTTS()
    except Exception:
        tts = None

    def speak(message):
        if tts is not None and message:
            try:
                tts.speak(message)
            except Exception:
                pass

    welcome = (
        "أهلًا بك في تيسير. اكتب أمرك أو اختر الصوت للتحدث. "
        "أستطيع قراءة الآيات، وتشغيل السور، وعرض التفسير، والبحث. "
        "اختر صفرًا لإنهاء المحادثة."
    )

    console.print(
        Panel(
            Text(ArabicText(welcome), justify="right"),
            title=ArabicText("۞ الوكيل الذكي لتيسير ۞"),
            border_style="green",
            padding=(1, 2),
        )
    )
    speak(welcome)

    ai_agent = None

    while True:
        mode = normalize_digits(
            console.input(
                f"\n[bold cyan]{ArabicText('1 كتابة | 2 صوت | 0 إنهاء: ')}[/]"
            ).strip()
        )

        if mode == "0":
            message = "انتهت المحادثة. شكرًا لاستخدام تيسير."
            show_message(console, message)
            speak(message)
            break

        if mode == "1":
            user_text = console.input(
                f"[bold cyan]{ArabicText('أنت: ')}[/]"
            ).strip()

        elif mode == "2":
            try:
                if voice_agent is None:
                    voice_agent = VoiceAgent()

                show_message(console, "تحدث الآن باللغة العربية لمدة 6 ثوانٍ...")
                user_text = voice_agent.listen()

                if not user_text:
                    message = "لم أتمكن من فهم كلامك. حاول مرة أخرى."
                    show_message(console, message, "yellow")
                    speak(message)
                    continue

                console.print(
                    f"[bold green]{ArabicText('سمعتك تقول:')}[/] "
                    f"{ArabicText(user_text)}"
                )

            except Exception as error:
                message = f"تعذّر تسجيل الصوت أو التعرف على الكلام: {error}"
                show_message(console, message, "yellow")
                speak(message)
                continue

        else:
            message = "اختر 1 للكتابة أو 2 للصوت أو 0 للإنهاء."
            show_message(console, message, "yellow")
            speak(message)
            continue

        if not user_text:
            continue

        normalized = normalize_arabic(user_text)
        if normalized in {"خروج", "انهاء", "انهاء المحادثه", "quit", "exit"}:
            break

        # نفّذ كل أمر محلي معروف عبر IntentParser ومعالج الأوامر نفسه.
        intent = parser.parse(user_text)
        if intent.action != "unknown":
            current_surah, current_ayah = handle_smart_command(
                console,
                parser,
                quran,
                tafsir,
                player,
                current_surah,
                current_ayah,
                command=user_text,
                intent_override=intent,
                voice_agent=voice_agent,
            )
            continue

        # الأسئلة العامة فقط تُرسل إلى نموذج الذكاء الاصطناعي.
        try:
            if ai_agent is None:
                ai_agent = TaysirAIAgent()

            context = build_quran_context(
                quran, tafsir, current_surah, current_ayah
            )

            try:
                result = ai_agent.understand(
                    user_text=user_text,
                    current_surah=current_surah,
                    current_ayah=current_ayah,
                    surah_names=build_surah_names(quran),
                    quran_context=context,
                )
            except TypeError:
                result = ai_agent.understand(
                    user_text=user_text,
                    current_surah=current_surah,
                    current_ayah=current_ayah,
                    surah_names=build_surah_names(quran),
                )

        except Exception as error:
            message = f"تعذّر الرد من خدمة الذكاء الاصطناعي: {error}"
            show_message(console, message, "yellow")
            speak(message)
            continue

        action = result.get("action", "chat")
        reply = (result.get("reply") or "").strip()

        if action == "exit":
            break

        if action in ("chat", "unknown"):
            if not reply:
                reply = (
                    "أستطيع مساعدتك في قراءة القرآن والتفسير والبحث "
                    "والتنقل بين الآيات وتشغيل التلاوة."
                )

            console.print(
                Panel(
                    Text(ArabicText(reply), justify="right"),
                    title=ArabicText("تيسير الذكي"),
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
            speak(reply)
            continue

        intent = SimpleNamespace(
            action=action,
            surah=result.get("surah"),
            ayah=result.get("ayah"),
            query=result.get("query", ""),
            play_audio=bool(result.get("play_audio", False)),
            repeats=result.get("repeats", 1),
        )

        current_surah, current_ayah = handle_smart_command(
            console,
            parser,
            quran,
            tafsir,
            player,
            current_surah,
            current_ayah,
            command=user_text,
            intent_override=intent,
            voice_agent=voice_agent,
        )

        if reply:
            speak(reply)

    return current_surah, current_ayah, voice_agent


def run_cli():
    console = Console()

    try:
        quran = QuranReader(QURAN_FILE)
        tafsir = TafsirReader(TAFSIR_FILE)
    except (OSError, ValueError) as error:
        show_message(console, f"تعذّر تحميل البيانات: {error}", "red")
        return

    if not quran.ayahs:
        show_message(console, "ملف القرآن لا يحتوي على آيات.", "red")
        return

    try:
        player = AudioPlayer()
    except Exception as error:
        show_message(console, f"تعذّر تهيئة مشغل الصوت: {error}", "red")
        return

    parser = IntentParser(build_surah_names(quran))
    current_surah = 1
    current_ayah = 1
    voice_agent = None

    try:
        show_header(console)

        console.print(
            f"[green]{ArabicText('تم تحميل')} "
            f"{quran.get_ayah_count()} {ArabicText('آية.')}[/]"
        )
        console.print(
            f"[green]{ArabicText('عدد التفسيرات المحمّلة:')} "
            f"{tafsir.get_count()}[/]"
        )

        show_current_ayah(console, quran, current_surah, current_ayah)

        while True:
            show_menu(console, MENU_OPTIONS)

            choice = normalize_digits(
                console.input(
                    f"\n[bold cyan]{ArabicText('اختر رقم العملية: ')}[/]"
                ).strip()
            )

            if choice == "0":
                show_message(console, "شكرًا لاستخدام تيسير.")
                break

            elif choice == "1":
                while True:
                    show_current_ayah(
                        console,
                        quran,
                        current_surah,
                        current_ayah,
                    )

                    # تشغيل تلاوة الآية الحالية
                    player.play_ayah(
                        current_surah,
                        current_ayah,
                        repeats=1,
                    )

                    reading_choice = normalize_digits(
                        console.input(
                            f"\n[bold cyan]{ArabicText('Enter للآية التالية، b للسابقة، q للعودة للقائمة: ')}[/]"
                        ).strip().lower()
                    )

                    if reading_choice == "q":
                        break

                    elif reading_choice == "b":
                        if current_ayah > 1:
                            current_ayah -= 1
                        elif current_surah > 1:
                            current_surah -= 1
                            previous_ayahs = quran.get_surah(current_surah)
                            if previous_ayahs:
                                current_ayah = previous_ayahs[-1]["ayah_number"]
                        else:
                            show_message(
                                console,
                                "أنت في بداية القرآن الكريم.",
                                "yellow",
                            )

                    elif reading_choice == "":
                        if quran.find(current_surah, current_ayah + 1):
                            current_ayah += 1
                        else:
                            next_surah = current_surah + 1
                            if next_surah <= 114 and quran.get_surah(next_surah):
                                current_surah = next_surah
                                current_ayah = 1
                            else:
                                show_message(
                                    console,
                                    "وصلت إلى نهاية القرآن الكريم.",
                                )
                                break

                    else:
                        show_message(
                            console,
                            "اضغط Enter للآية التالية، أو b للسابقة، أو q للعودة.",
                            "yellow",
                        )

            elif choice == "2":
                if quran.find(current_surah, current_ayah + 1):
                    current_ayah += 1
                else:
                    next_surah = current_surah + 1
                    while next_surah <= 114 and not quran.find(next_surah, 1):
                        next_surah += 1

                    if next_surah > 114:
                        show_message(console, "وصلت إلى نهاية القرآن الكريم.", "yellow")
                        continue

                    current_surah, current_ayah = next_surah, 1

                show_current_ayah(console, quran, current_surah, current_ayah)

            elif choice == "3":
                if current_ayah > 1:
                    current_ayah -= 1
                elif current_surah > 1:
                    previous_surah = current_surah - 1
                    while previous_surah > 1 and not quran.get_surah(previous_surah):
                        previous_surah -= 1

                    previous_ayahs = quran.get_surah(previous_surah)
                    if previous_ayahs:
                        current_surah = previous_surah
                        current_ayah = previous_ayahs[-1]["ayah_number"]
                else:
                    show_message(console, "أنت في بداية القرآن الكريم.", "yellow")
                    continue

                show_current_ayah(console, quran, current_surah, current_ayah)

            elif choice == "4":
                try:
                    surah = int(normalize_digits(console.input(
                        ArabicText("أدخل رقم السورة: ")
                    ).strip()))
                    ayah = int(normalize_digits(console.input(
                        ArabicText("أدخل رقم الآية: ")
                    ).strip()))
                except ValueError:
                    show_message(console, "أدخل أرقامًا صحيحة.", "yellow")
                    continue

                if quran.find(surah, ayah) is None:
                    show_message(console, "السورة أو الآية غير موجودة.", "yellow")
                    continue

                current_surah, current_ayah = surah, ayah
                show_current_ayah(console, quran, current_surah, current_ayah)

            elif choice == "5":
                if quran.find(current_surah, current_ayah) is None:
                    show_message(console, "لم يتم العثور على الآية الحالية.", "yellow")
                    continue

                repeats = ask_repeat_count(console)
                player.play_ayah(
                    current_surah,
                    current_ayah,
                    repeats=repeats,
                )

            elif choice == "6":
                show_tafsir(console, tafsir, current_surah, current_ayah)

            elif choice == "7":
                search_ayahs(console, quran)

            elif choice == "8":
                show_help(console)

            elif choice == "9":
                player.play_ayah(current_surah, current_ayah, repeats=3)

            elif choice == "10":
                player.play_surah(quran.get_surah(current_surah))

            elif choice == "11":
                player.stop()
                show_message(console, "تم إيقاف التلاوة.")

            elif choice == "12":
                (
                    current_surah,
                    current_ayah,
                    voice_agent,
                ) = run_ai_agent_chat(
                    console,
                    quran,
                    tafsir,
                    player,
                    parser,
                    current_surah,
                    current_ayah,
                    voice_agent=voice_agent,
                )

            else:
                show_message(console, "اختيار غير صحيح. حاول مرة أخرى.", "yellow")

    except KeyboardInterrupt:
        show_message(console, "تم إيقاف البرنامج.")

    finally:
        player.close()


if __name__ == "__main__":
    run_cli()
