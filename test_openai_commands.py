import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not API_KEY:
    raise SystemExit(
        "لم يتم العثور على OPENAI_API_KEY في ملف .env"
    )

client = OpenAI(api_key=API_KEY)

ACTIONS = [
    "read",
    "next",
    "previous",
    "goto",
    "tafsir",
    "repeat",
    "search",
    "play_ayah",
    "play_surah",
    "stop",
    "help",
    "exit",
    "chat",
]

SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ACTIONS,
        },
        "surah": {
            "type": ["integer", "null"],
        },
        "ayah": {
            "type": ["integer", "null"],
        },
        "query": {
            "type": "string",
        },
        "reply": {
            "type": "string",
        },
    },
    "required": [
        "action",
        "surah",
        "ayah",
        "query",
        "reply",
    ],
    "additionalProperties": False,
}

INSTRUCTIONS = """
أنت محلل أوامر لتطبيق تيسير، وهو تطبيق لقراءة القرآن الكريم.

افهم العربية الفصحى واللهجة السعودية والأوامر القصيرة.

صنّف الأمر إلى إجراء واحد فقط من القائمة:

read: عرض الآية الحالية.
next: الانتقال إلى الآية التالية.
previous: الانتقال إلى الآية السابقة.
goto: الانتقال إلى سورة وآية محددتين.
tafsir: عرض التفسير الميسر من بيانات التطبيق المحلية.
repeat: إعادة عرض الآية الحالية.
search: البحث عن عبارة في نص القرآن.
play_ayah: تشغيل الآية الحالية صوتياً.
play_surah: تشغيل سورة كاملة صوتياً.
stop: إيقاف التلاوة.
help: عرض المساعدة.
exit: إنهاء المحادثة.
chat: سؤال عام أو أمر غير واضح.

قواعد مهمة:

1. "اقرأ سورة البقرة" تعني play_surah، أي تشغيل السورة كاملة.
2. "اعرض سورة البقرة آية 5" تعني goto، أي الانتقال إلى الآية دون تشغيل الصوت.
3. "انتقل إلى سورة الملك الآية الخامسة" تعني goto، مع surah=67 وayah=5.
4. "فسّر لي الآية الحالية" تعني tafsir.
5. "شغّل الآية الحالية" تعني play_ayah.
6. "أوقف التلاوة" تعني stop.
7. لا تخترع آيات أو تفاسير.
8. لا تنفذ أي إجراء؛ مهمتك تصنيف الأمر فقط.
9. إذا كان الأمر غامضاً، اختر chat واطلب توضيحاً قصيراً.
10. إذا لم يذكر المستخدم سورة أو آية، استخدم null للأرقام غير المحددة.
11. query يحتوي عبارة البحث عند استخدام search، وإلا يكون نصاً فارغاً.
12. reply رد عربي مختصر عند الحاجة، وإلا نص فارغ.

أعد البيانات وفق مخطط JSON المطلوب فقط.
"""


def classify_command(user_text):
    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=user_text,
        text={
            "format": {
                "type": "json_schema",
                "name": "taysir_command",
                "strict": True,
                "schema": SCHEMA,
            }
        },
    )

    if not response.output_text:
        raise RuntimeError("لم يُرجع OpenAI نتيجة نصية.")

    result = json.loads(response.output_text)

    if result["action"] not in ACTIONS:
        raise ValueError("الإجراء الناتج غير مدعوم.")

    return result


def main():
    print("اختبار فهم أوامر تيسير باستخدام OpenAI")
    print(f"النموذج: {MODEL}")
    print("اكتب (خروج) لإنهاء الاختبار.\n")

    while True:
        try:
            command = input("أنت: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nانتهى الاختبار.")
            break

        if command in {"خروج", "إنهاء", "exit", "quit"}:
            print("انتهى الاختبار.")
            break

        if not command:
            continue

        try:
            result = classify_command(command)

            print("\nنتيجة التصنيف:")
            print(json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            ))
            print("\n" + "-" * 40 + "\n")

        except Exception as error:
            print(
                f"\nتعذر اختبار الأمر: "
                f"{type(error).__name__}: {error}\n"
            )


if __name__ == "__main__":
    main()
