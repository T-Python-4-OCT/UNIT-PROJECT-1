import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("لم يتم العثور على OPENAI_API_KEY في ملف .env")
    sys.exit(1)

audio_path = (
    Path(sys.argv[1]).expanduser()
    if len(sys.argv) > 1
    else None
)

if audio_path is None or not audio_path.is_file():
    print("طريقة الاستخدام:")
    print("python test_openai_speech.py /path/to/audio.wav")
    sys.exit(1)

try:
    client = OpenAI(api_key=api_key)

    with audio_path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(
            model="gpt-transcribe",
            file=audio_file,
            prompt=(
                "المتحدث يتحدث بالعربية السعودية. "
                "السياق تطبيق قرآن اسمه تيسير. "
                "قد يذكر أسماء السور والآيات وأوامر تشغيل التلاوة."
            ),
        )

    print("\nالنص الذي تعرّف عليه OpenAI:")
    print(result.text)

except Exception as error:
    print(f"\nفشل الاختبار: {type(error).__name__}: {error}")
