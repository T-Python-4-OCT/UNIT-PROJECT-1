
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_FILE = BASE_DIR / "data" / "hafs_smart_v8.json"
OUTPUT_FILE = BASE_DIR / "data" / "quran.json"


def convert_quran_data():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"لم يتم العثور على الملف: {SOURCE_FILE}"
        )

    with SOURCE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("يجب أن تكون بيانات المصدر قائمة.")

    ayahs = []
    seen = set()

    required = {
        "sura_no",
        "sura_name_ar",
        "aya_no",
        "aya_text",
        "aya_text_emlaey",
    }

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("يوجد عنصر غير صالح في ملف المصدر.")

        if not required.issubset(item):
            missing = required - item.keys()
            raise ValueError(
                f"حقول مفقودة في أحد العناصر: {missing}"
            )

        try:
            surah_number = int(item["sura_no"])
            ayah_number = int(item["aya_no"])
        except (ValueError, TypeError):
            raise ValueError(
                "يوجد رقم سورة أو آية غير صالح."
            ) from None

        surah_name = item["sura_name_ar"]
        text = item["aya_text_emlaey"]
        smart_text = item["aya_text"]

        if not 1 <= surah_number <= 114:
            raise ValueError(
                f"رقم سورة غير صالح: {surah_number}"
            )

        if ayah_number < 1:
            raise ValueError(
                f"رقم آية غير صالح: {ayah_number}"
            )

        if not isinstance(surah_name, str) or not surah_name.strip():
            raise ValueError("اسم السورة فارغ أو غير صالح.")

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"النص الإملائي فارغ في السورة {surah_number}، "
                f"الآية {ayah_number}."
            )

        if not isinstance(smart_text, str) or not smart_text.strip():
            raise ValueError(
                f"النص الأصلي فارغ في السورة {surah_number}، "
                f"الآية {ayah_number}."
            )

        key = (surah_number, ayah_number)

        if key in seen:
            raise ValueError(
                f"آية مكررة: السورة {surah_number}، "
                f"الآية {ayah_number}."
            )

        seen.add(key)

        ayahs.append({
            "surah_number": surah_number,
            "surah_name": surah_name,
            "ayah_number": ayah_number,
            "text": text,
            "text_smart": smart_text,
        })

    ayahs.sort(
        key=lambda item: (
            item["surah_number"],
            item["ayah_number"],
        )
    )

    # التحقق من تسلسل أرقام الآيات داخل كل سورة.
    expected_next = {}

    for ayah in ayahs:
        surah = ayah["surah_number"]
        number = ayah["ayah_number"]

        expected = expected_next.get(surah, 1)

        if number != expected:
            raise ValueError(
                f"تسلسل الآيات غير مكتمل في السورة {surah}: "
                f"المتوقع {expected}، الموجود {number}."
            )

        expected_next[surah] = number + 1

    if len(ayahs) != 6236:
        raise ValueError(
            f"عدد العناصر {len(ayahs)} وليس 6236. "
            "راجع المصدر قبل اعتماد البيانات."
        )

    if set(expected_next) != set(range(1, 115)):
        raise ValueError(
            "البيانات لا تحتوي على السور الـ114 كاملة."
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            ayahs,
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.write("\n")

    print("اكتمل تحويل البيانات بنجاح.")
    print(f"عدد الآيات: {len(ayahs)}")
    print(f"عدد السور: {len(expected_next)}")
    print(f"الملف الناتج: {OUTPUT_FILE}")


if __name__ == "__main__":
    convert_quran_data()
