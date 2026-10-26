"""التعرف على الكلام العربي باستخدام واجهة Munsit."""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

MUNSIT_API_URL = "https://api.munsit.com/api/v1/audio/transcribe"


class MunsitSTT:
    """إرسال التسجيل الصوتي إلى Munsit وإرجاع النص العربي."""

    def __init__(self):
        self.api_key = os.getenv("MUNSIT_API_KEY", "").strip()

        if not self.api_key:
            raise RuntimeError(
                "لم يتم العثور على MUNSIT_API_KEY في ملف .env."
            )

    def transcribe(self, audio_path):
        """تحويل ملف صوتي إلى نص عربي."""

        audio_path = Path(audio_path)

        if not audio_path.is_file():
            raise FileNotFoundError(
                f"ملف الصوت غير موجود: {audio_path}"
            )

        headers = {
            "x-api-key": self.api_key,
        }

        try:
            with audio_path.open("rb") as audio_file:
                response = requests.post(
                    MUNSIT_API_URL,
                    headers=headers,
                    files={
                        "file": (
                            audio_path.name,
                            audio_file,
                            "audio/wav",
                        )
                    },
                    data={"model": "munsit"},
                    timeout=120,
                )

            response.raise_for_status()
            result = response.json()

        except requests.RequestException as error:
            raise RuntimeError(
                f"فشل الاتصال بخدمة Munsit: {error}"
            ) from error

        data = result.get("data", {})
        text = data.get("transcription", "")

        if not isinstance(text, str) or not text.strip():
            raise RuntimeError(
                f"لم تُرجع Munsit نصًا صالحًا. الاستجابة: {result}"
            )

        return text.strip()
