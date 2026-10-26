
import json
from pathlib import Path


class TafsirReader:
    """قراءة التفسير الميسّر من ملف JSON."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.tafsir = self._load()

    def _load(self):
        # إذا لم يوجد الملف، نرجع قاموسًا فارغًا.
        if not self.file_path.exists():
            return {}

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(
                f"تعذّرت قراءة ملف التفسير: {error}"
            ) from error

        if not isinstance(data, list):
            raise ValueError(
                "يجب أن يحتوي tafsir.json على قائمة."
            )

        tafsir = {}

        for item in data:
            if not isinstance(item, dict):
                raise ValueError(
                    "يوجد مدخل غير صالح في التفسير."
                )

            required = {
                "surah_number",
                "ayah_number",
                "text",
            }

            if not required.issubset(item):
                raise ValueError(
                    "حقول مفقودة في أحد التفسيرات."
                )

            try:
                surah = int(item["surah_number"])
                ayah = int(item["ayah_number"])
            except (ValueError, TypeError):
                raise ValueError(
                    "رقم السورة أو الآية غير صالح."
                ) from None

            text = item["text"]

            if not 1 <= surah <= 114 or ayah < 1:
                raise ValueError(
                    f"رقم آية غير صالح: {surah}:{ayah}"
                )

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    f"نص التفسير فارغ: {surah}:{ayah}"
                )

            key = (surah, ayah)

            if key in tafsir:
                raise ValueError(
                    f"تفسير مكرر للآية: {surah}:{ayah}"
                )

            tafsir[key] = text.strip()

        return tafsir

    def get(self, surah_number, ayah_number):
        """إرجاع تفسير آية محددة، أو None إذا لم يوجد."""

        try:
            key = (int(surah_number), int(ayah_number))
        except (ValueError, TypeError):
            return None

        return self.tafsir.get(key)

    def get_count(self):
        """إرجاع عدد التفسيرات المحمّلة."""

        return len(self.tafsir)
