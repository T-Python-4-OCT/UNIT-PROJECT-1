
import gzip
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

SOURCE_FILE = DATA_DIR / "tafsir_source.json.gz"
OUTPUT_FILE = DATA_DIR / "tafsir.json"

EXPECTED_AYAH_COUNT = 6236


def convert_tafsir():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"لم يتم العثور على المصدر: {SOURCE_FILE}"
        )

    print("جارٍ قراءة بيانات التفسير...")

    with gzip.open(SOURCE_FILE, "rt", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("صيغة ملف المصدر غير صحيحة.")

    book = data.get("book", {})
    ayahs = data.get("ayahs")

    if book.get("id") != 2012:
        raise ValueError(
            "معرّف الكتاب لا يطابق معرّف التفسير الميسّر المتوقع."
        )

    if not isinstance(ayahs, list):
        raise ValueError("حقل ayahs ليس قائمة.")

    if len(ayahs) != EXPECTED_AYAH_COUNT:
        raise ValueError(
            f"عدد المداخل {len(ayahs)}، "
            f"والمتوقع {EXPECTED_AYAH_COUNT}."
        )

    tafsir_data = []
    seen = set()

    for item in ayahs:
        if not isinstance(item, dict):
            raise ValueError("يوجد مدخل غير صالح في المصدر.")

        if not {"surah", "ayah", "content"}.issubset(item):
            raise ValueError("هناك حقول أساسية مفقودة في أحد المداخل.")

        try:
            surah_number = int(item["surah"])
            ayah_number = int(item["ayah"])
        except (ValueError, TypeError):
            raise ValueError("رقم سورة أو آية غير صالح.") from None

        if not 1 <= surah_number <= 114:
            raise ValueError(f"رقم سورة غير صالح: {surah_number}")

        if ayah_number < 1:
            raise ValueError(f"رقم آية غير صالح: {ayah_number}")

        key = (surah_number, ayah_number)

        if key in seen:
            raise ValueError(
                f"تفسير مكرر للسورة {surah_number}، "
                f"الآية {ayah_number}."
            )

        content = item["content"]

        if not isinstance(content, list) or not content:
            raise ValueError(
                f"لا يوجد محتوى تفسير للآية {surah_number}:{ayah_number}."
            )

        text_parts = []

        for part in content:
            if not isinstance(part, dict):
                raise ValueError(
                    f"محتوى غير صالح للآية {surah_number}:{ayah_number}."
                )

            text = part.get("text")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    f"نص تفسير فارغ للآية {surah_number}:{ayah_number}."
                )

            text_parts.append(text.strip())

        seen.add(key)

        tafsir_data.append({
            "surah_number": surah_number,
            "ayah_number": ayah_number,
            "text": "\n".join(text_parts),
        })

    tafsir_data.sort(
        key=lambda item: (
            item["surah_number"],
            item["ayah_number"],
        )
    )

    if len(tafsir_data) != EXPECTED_AYAH_COUNT:
        raise ValueError("عدد التفسيرات النهائي غير صحيح.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            tafsir_data,
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.write("\n")

    print("\nاكتمل تحويل التفسير بنجاح.")
    print(f"اسم الكتاب: {book.get('name', 'غير معروف')}")
    print(f"المؤلف: {book.get('author', {}).get('ar_name', 'غير معروف')}")
    print(f"عدد التفسيرات: {len(tafsir_data)}")
    print(f"الملف الناتج: {OUTPUT_FILE}")


if __name__ == "__main__":
    convert_tafsir()
