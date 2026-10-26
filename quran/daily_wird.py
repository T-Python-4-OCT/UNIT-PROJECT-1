
"""إدارة الورد القرآني اليومي وربطه بـ n8n."""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

QURAN_FILE = BASE_DIR / "data" / "hafs_smart_v8.json"
PROGRESS_FILE = BASE_DIR / "data" / "daily_wird_progress.json"

PAGES_PER_DAY = 2
TOTAL_PAGES = 604
WEBHOOK_URL = os.getenv("TAYSIR_PROGRESS_WEBHOOK_URL", "").strip()


def load_ayahs():
    with open(QURAN_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_progress():
    if not PROGRESS_FILE.exists():
        return {"start_page": 1, "completed_days": 0}

    with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_progress(progress):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        json.dump(progress, file, ensure_ascii=False, indent=2)


def get_daily_wird():
    progress = load_progress()
    start_page = progress["start_page"]

    if start_page > TOTAL_PAGES:
        return {"finished": True, "ayahs": []}

    end_page = min(start_page + PAGES_PER_DAY - 1, TOTAL_PAGES)

    ayahs = [
        ayah for ayah in load_ayahs()
        if start_page <= ayah["page"] <= end_page
    ]
    ayahs.sort(key=lambda ayah: ayah["id"])

    return {
        "finished": False,
        "start_page": start_page,
        "end_page": end_page,
        "ayahs": ayahs,
        "completed_days": progress["completed_days"],
    }


def send_progress_to_n8n(payload):
    """إرسال التقدم إلى n8n دون تعطيل الحفظ المحلي عند فشل الاتصال."""
    if not WEBHOOK_URL:
        print("ملاحظة: لم يُضبط رابط Webhook؛ حُفظ التقدم محليًا فقط.")
        return

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        print("تم إرسال تحديث الورد إلى n8n.")
    except requests.RequestException as error:
        print("تعذر إرسال التحديث إلى n8n، لكن التقدم المحلي محفوظ.")
        print(f"تفاصيل الاتصال: {error}")


def complete_daily_wird():
    progress = load_progress()
    start_page = progress["start_page"]

    if start_page > TOTAL_PAGES:
        return False

    end_page = min(start_page + PAGES_PER_DAY - 1, TOTAL_PAGES)

    progress["start_page"] = min(
        end_page + 1,
        TOTAL_PAGES + 1,
    )
    progress["completed_days"] += 1

    # حفظ التقدم محليًا أولًا.
    save_progress(progress)

    # إرسال ملخص التقدم بعد الحفظ.
    send_progress_to_n8n({
        "event": "daily_wird_completed",
        "pages_completed": {
            "from": start_page,
            "to": end_page,
        },
        "next_start_page": progress["start_page"],
        "completed_days": progress["completed_days"],
        "pages_per_day": PAGES_PER_DAY,
    })

    return True


def main():
    wird = get_daily_wird()

    if wird["finished"]:
        print("ما شاء الله، أكملت صفحات المصحف كلها!")
        return

    print(
        f"الورد اليومي: الصفحات "
        f"{wird['start_page']}–{wird['end_page']}\n"
    )

    for ayah in wird["ayahs"]:
        print(
            f"سورة {ayah['sura_name_ar']} - "
            f"آية {ayah['aya_no']}: {ayah['aya_text_emlaey']}"
        )

    print(f"\nعدد الآيات: {len(wird['ayahs'])}")
    print(f"الأيام المكتملة: {wird['completed_days']}")

    answer = input("\nهل أكملت قراءة الورد؟ (نعم/لا): ").strip()

    if answer == "نعم":
        if complete_daily_wird():
            print("تقبل الله منك! تم حفظ تقدمك.")
    else:
        print("لم يتغير تقدمك. يمكنك إكمال الورد لاحقًا.")


if __name__ == "__main__":
    main()
