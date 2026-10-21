import re
import unicodedata
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Intent:
    action: str
    surah: Optional[int] = None
    ayah: Optional[int] = None
    query: Optional[str] = None


class IntentParser:
    """تحليل الأوامر العربية البسيطة الخاصة بتطبيق تيسير."""

    ACTIONS = {
        "read": ("اقرا", "اقرأ", "اعرض الايه", "اعرض الآيه"),
        "next": ("التالي", "الايه التاليه", "الآية التالية",
                 "الايه اللي بعدها", "الآية اللي بعدها"),
        "previous": ("السابق", "الايه السابقه", "الآية السابقة",
                     "الايه اللي قبلها", "الآية اللي قبلها"),
        "tafsir": ("التفسير", "فسر الايه", "فسر الآيه",
                   "اعرض التفسير", "التفسير الميسر"),
        "repeat": ("كرر الايه", "كرر الآيه", "اعادة الايه",
                   "إعادة الآية", "اعرض الايه مره ثانيه"),
        "play_ayah": ("استمع للايه", "شغل الايه", "شغل الآيه",
                      "استمع للآيه"),
        "play_surah": ("استمع للسوره", "شغل السوره",
                       "شغل السورة", "استمع للسورة"),
        "stop": ("اوقف التلاوه", "وقف التلاوه", "اوقف الصوت",
                 "وقف الصوت", "ايقاف التلاوه"),
        "help": ("مساعده", "المساعده", "ساعدني"),
        "exit": ("خروج", "اخرج", "انهاء البرنامج"),
    }

    def __init__(self, surah_names=None):
        self.surah_names = surah_names or {}

    @staticmethod
    def normalize(text):
        text = unicodedata.normalize("NFKC", text).strip().lower()

        replacements = str.maketrans({
            "أ": "ا",
            "إ": "ا",
            "آ": "ا",
            "ٱ": "ا",
            "ى": "ي",
            "ؤ": "و",
            "ئ": "ي",
            "ة": "ه",
            "٠": "0",
            "١": "1",
            "٢": "2",
            "٣": "3",
            "٤": "4",
            "٥": "5",
            "٦": "6",
            "٧": "7",
            "٨": "8",
            "٩": "9",
        })
        text = text.translate(replacements)

        text = "".join(
            char for char in text
            if unicodedata.category(char) not in ("Mn", "Me")
        )
        text = re.sub(r"[،,؛;.!؟?]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _find_surah(self, text):
        normalized_text = self.normalize(text)

        for number, name in self.surah_names.items():
            normalized_name = self.normalize(str(name))
            if normalized_name and normalized_name in normalized_text:
                return int(number)

        return None

    @staticmethod
    def _find_numbers(text):
        return [
            int(number)
            for number in re.findall(r"(?<!\w)\d+(?!\w)", text)
        ]

    def parse(self, text):
        if not isinstance(text, str) or not text.strip():
            return Intent("unknown")

        normalized = self.normalize(text)

        # البحث عن آية أو عبارة قرآنية.
        search_match = re.search(
            r"(?:ابحث|بحث|دور)\s+(?:عن|في)\s+(.+)",
            normalized,
        )
        if search_match:
            return Intent(
                "search",
                query=search_match.group(1).strip(),
            )

        # الانتقال إلى سورة وآية محددتين.
        if any(word in normalized for word in (
            "انتقل", "اذهب", "روح", "الانتقال", "افتح"
        )):
            surah = self._find_surah(normalized)
            numbers = self._find_numbers(normalized)

            if surah is not None:
                ayah = numbers[-1] if numbers else None
                return Intent("goto", surah=surah, ayah=ayah)

            if len(numbers) >= 2:
                return Intent(
                    "goto",
                    surah=numbers[0],
                    ayah=numbers[1],
                )

        # أوامر التنقل العامة.
        for action in ("next", "previous", "tafsir", "repeat",
                       "play_ayah", "play_surah", "stop", "help", "exit"):
            for phrase in self.ACTIONS[action]:
                if self.normalize(phrase) in normalized:
                    return Intent(action)

        # قراءة آية أو عرض الآية الحالية.
        if any(word in normalized for word in (
            "اقرا", "اعرض الايه", "الايه الحاليه"
        )):
            return Intent("read")

        return Intent("unknown")
