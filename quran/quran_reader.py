
import json
import unicodedata
from pathlib import Path


class QuranReader:
    """قراءة القرآن الكريم والبحث في الآيات."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.ayahs = self._load()

    @staticmethod
    def _normalize_arabic(text):
        """توحيد بعض الحروف لتسهيل البحث."""

        text = unicodedata.normalize("NFC", text)
        normalized = []

        for char in text:
            if unicodedata.category(char) in ("Mn", "Me"):
                continue

            if char == "\u0640":
                continue

            if char in "أإآٱ":
                char = "ا"
            elif char == "ى":
                char = "ي"

            normalized.append(char)

        return "".join(normalized).strip()

    def _load(self):
        """تحميل الآيات من ملف JSON."""

        # إذا لم يوجد الملف، نرجع قائمة فارغة.
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(
                f"تعذّرت قراءة ملف القرآن: {error}"
            ) from error

        if not isinstance(data, list):
            raise ValueError(
                "يجب أن يحتوي quran.json على قائمة من الآيات."
            )

        required = {
            "surah_number",
            "surah_name",
            "ayah_number",
            "text",
        }

        ayahs = []
        seen = set()

        for item in data:
            if not isinstance(item, dict):
                raise ValueError("يوجد عنصر غير صالح في ملف القرآن.")

            if not required.issubset(item):
                raise ValueError(
                    f"حقول مفقودة: {required - item.keys()}"
                )

            try:
                surah = int(item["surah_number"])
                ayah = int(item["ayah_number"])
            except (ValueError, TypeError):
                raise ValueError(
                    "رقم السورة أو الآية غير صالح."
                ) from None

            name = item["surah_name"]
            text = item["text"]

            if not 1 <= surah <= 114:
                raise ValueError(f"رقم السورة غير صالح: {surah}")

            if ayah < 1:
                raise ValueError(f"رقم الآية غير صالح: {ayah}")

            if not isinstance(name, str) or not name.strip():
                raise ValueError("اسم السورة فارغ.")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"نص الآية فارغ: {surah}:{ayah}")

            key = (surah, ayah)

            if key in seen:
                raise ValueError(f"آية مكررة: {surah}:{ayah}")

            seen.add(key)

            normalized_item = dict(item)
            normalized_item["surah_number"] = surah
            normalized_item["ayah_number"] = ayah
            ayahs.append(normalized_item)

        ayahs.sort(
            key=lambda item: (
                item["surah_number"],
                item["ayah_number"],
            )
        )

        return ayahs

    def find(self, surah_number, ayah_number):
        """العثور على آية محددة."""

        try:
            surah_number = int(surah_number)
            ayah_number = int(ayah_number)
        except (ValueError, TypeError):
            return None

        for item in self.ayahs:
            if (
                item["surah_number"] == surah_number
                and item["ayah_number"] == ayah_number
            ):
                return item

        return None

    def get_surah(self, surah_number):
        """إرجاع جميع آيات سورة محددة."""

        try:
            surah_number = int(surah_number)
        except (ValueError, TypeError):
            return []

        return [
            item
            for item in self.ayahs
            if item["surah_number"] == surah_number
        ]

    def search(self, query):
        """البحث في الآيات وأسماء السور."""

        if not isinstance(query, str):
            return []

        query = self._normalize_arabic(query)

        if not query:
            return []

        results = []

        for item in self.ayahs:
            text = self._normalize_arabic(item["text"])
            name = self._normalize_arabic(item["surah_name"])
            smart_text = self._normalize_arabic(
                item.get("text_smart", "")
            )

            if (
                query in text
                or query in name
                or query in smart_text
            ):
                results.append(item)

        return results

    def get_surah_count(self):
        """عدد السور الموجودة في البيانات."""

        return len({
            item["surah_number"]
            for item in self.ayahs
        })

    def get_ayah_count(self):
        """عدد الآيات الموجودة في البيانات."""

        return len(self.ayahs)
