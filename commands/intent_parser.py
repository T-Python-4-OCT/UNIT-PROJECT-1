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
    play_audio: bool = False
    repeats: int = 1


class IntentParser:
    """تحليل أوامر تيسير مع الفصل بين العرض والتلاوة."""

    def __init__(self, surah_names=None):
        self.surah_names = surah_names or {}

    @staticmethod
    def normalize(text):
        text = unicodedata.normalize("NFKC", str(text or "")).strip().lower()

        text = text.translate(str.maketrans(
            "أإآٱىؤئة٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
            "اااايويه01234567890123456789",
        ))

        text = "".join(
            char for char in text
            if unicodedata.category(char) not in ("Mn", "Me")
        )

        text = re.sub(r"[،,؛;.!؟?():]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _find_surah(self, text):
        normalized = self.normalize(text)

        for number, name in sorted(
            self.surah_names.items(),
            key=lambda item: len(self.normalize(item[1])),
            reverse=True,
        ):
            normalized_name = self.normalize(name)

            if normalized_name and re.search(
                r"(?<!\w)" + re.escape(normalized_name) + r"(?!\w)",
                normalized,
            ):
                return int(number)

        match = re.search(
            r"(?:السوره|سوره)\s*(?:رقم\s*)?(\d+)",
            normalized,
        )

        if match:
            number = int(match.group(1))
            if 1 <= number <= 114:
                return number

        return None

    @staticmethod
    def _find_ayah(text):
        match = re.search(
            r"(?:الاية|الايه|ايه|اية)\s*(?:رقم\s*)?(\d+)",
            text,
        )
        return int(match.group(1)) if match else None

    @staticmethod
    def _repeat_count(text):
        match = re.search(r"(\d+)\s*(?:مرات|مره)", text)

        if match:
            return max(1, min(int(match.group(1)), 100))

        if "مرتين" in text:
            return 2

        for word, count in (
            ("ثلاث", 3),
            ("ثلاثه", 3),
            ("اربع", 4),
            ("اربعه", 4),
            ("خمس", 5),
            ("خمسه", 5),
            ("ست", 6),
            ("سته", 6),
            ("سبع", 7),
            ("سبعه", 7),
            ("ثمان", 8),
            ("ثمانيه", 8),
            ("تسع", 9),
            ("تسعه", 9),
            ("عشر", 10),
            ("عشره", 10),
        ):
            if re.search(r"(?<!\w)" + word + r"(?!\w)", text):
                return count

        return 1

    def parse(self, text):
        if not isinstance(text, str) or not text.strip():
            return Intent("unknown")

        normalized = self.normalize(text)
        surah = self._find_surah(normalized)
        ayah = self._find_ayah(normalized)
        repeats = self._repeat_count(normalized)

        # إيقاف الصوت.
        if any(phrase in normalized for phrase in (
            "اوقف التلاوه",
            "وقف التلاوه",
            "اوقف الصوت",
            "وقف الصوت",
            "ايقاف التلاوه",
        )):
            return Intent("stop")

        # البحث.
        search_match = re.search(
            r"(?:ابحث|بحث|دور|فتش)\s+(?:عن|في)\s+(.+)",
            normalized,
        )

        if search_match:
            return Intent(
                "search",
                query=search_match.group(1).strip(),
            )

        # المساعدة والخروج.
        if any(phrase in normalized for phrase in (
            "ساعدني", "المساعده", "مساعده"
        )):
            return Intent("help")

        if normalized in (
            "خروج", "اخرج", "انهاء البرنامج", "quit", "exit"
        ):
            return Intent("exit")

        # التفسير له الأولوية على القراءة والتشغيل.
        if any(word in normalized for word in (
            "تفسير", "فسر", "اشرح", "معنى الايه"
        )):
            if surah is not None and ayah is not None:
                return Intent("tafsir", surah=surah, ayah=ayah)

            if surah is not None:
                return Intent("tafsir_surah", surah=surah)

            return Intent("tafsir")

        # التكرار يعني تشغيل الصوت.
        if any(word in normalized for word in (
            "كرر", "تكرار", "اعاده", "اعد"
        )):
            return Intent(
                "repeat",
                surah=surah,
                ayah=ayah,
                play_audio=True,
                repeats=repeats,
            )

        # أوامر التلاوة. تحديد الآية يسبق تشغيل السورة.
        audio_verbs = (
            "اقرا", "قراءه", "تلاوه",
            "شغل", "اسمع", "استمع",
        )

        asks_audio = any(
            re.search(r"(?<!\w)" + verb + r"(?!\w)", normalized)
            for verb in audio_verbs
        )

        if asks_audio:
            if ayah is not None:
                return Intent(
                    "play_ayah",
                    surah=surah,
                    ayah=ayah,
                    play_audio=True,
                    repeats=repeats,
                )

            if surah is not None:
                return Intent(
                    "play_surah",
                    surah=surah,
                    play_audio=True,
                    repeats=repeats,
                )

            return Intent(
                "play_ayah",
                play_audio=True,
                repeats=repeats,
            )

        # العرض والتنقل لا يشغّلان الصوت.
        display_verbs = (
            "اعرض", "انتقل", "افتح",
            "اذهب", "روح", "ودني", "انقلني",
        )

        asks_display = any(
            re.search(r"(?<!\w)" + verb + r"(?!\w)", normalized)
            for verb in display_verbs
        )

        if asks_display:
            if surah is not None and ayah is not None:
                return Intent("goto", surah=surah, ayah=ayah)

            if surah is not None:
                return Intent("show_surah", surah=surah)

            if ayah is not None:
                return Intent("goto", ayah=ayah)

            if any(phrase in normalized for phrase in (
                "التالي", "اللي بعدها", "التي بعدها",
                "الجايه", "القادمه",
            )):
                return Intent("next")

            if any(phrase in normalized for phrase in (
                "السابق", "اللي قبلها", "التي قبلها",
            )):
                return Intent("previous")

        # التنقل العام.
        if any(phrase in normalized for phrase in (
            "التالي", "الايه التاليه", "الايه اللي بعدها",
        )):
            return Intent("next")

        if any(phrase in normalized for phrase in (
            "السابق", "الايه السابقه", "الايه اللي قبلها",
        )):
            return Intent("previous")

        # رقم السورة والآية دون فعل صريح.
        if surah is not None and ayah is not None:
            return Intent("goto", surah=surah, ayah=ayah)

        if any(phrase in normalized for phrase in (
            "الايه الحاليه", "اعرض الايه",
        )):
            return Intent("read")

        if normalized in ("التفسير", "التفسير الميسر"):
            return Intent("tafsir")

        return Intent("unknown")
