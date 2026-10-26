from pathlib import Path

from ai_agent import TaysirAIAgent
from quran.quran_reader import QuranReader

BASE_DIR = Path(__file__).resolve().parent
QURAN_FILE = BASE_DIR / "data" / "quran.json"

quran = QuranReader(str(QURAN_FILE))
agent = TaysirAIAgent()

surah_names = {
    ayah["surah_number"]: ayah["surah_name"]
    for ayah in quran.ayahs
}

commands = [
    "اقرأ سورة البقرة آية رقم 286",
    "انتقل إلى سورة الملك الآية الخامسة",
    "وش تفسير الآية الحالية؟",
    "أوقف التلاوة",
]

for command in commands:
    print(f"\nأنت: {command}")

    try:
        result = agent.understand(
            user_text=command,
            current_surah=1,
            current_ayah=1,
            surah_names=surah_names,
        )
        print("الوكيل:", result)
    except Exception as error:
        print(f"خطأ: {type(error).__name__}: {error}")

