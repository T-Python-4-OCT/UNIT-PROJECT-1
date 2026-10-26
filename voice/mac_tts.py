
"""تحويل النص العربي إلى كلام باستخدام صوت macOS المحلي."""

import subprocess


class MacTTS:
    """مشغل صوت المساعد باستخدام صوت ماجد."""

    def __init__(self, voice: str = "Majed"):
        self.voice = voice

    def speak(self, text: str) -> None:
        """نطق النص باستخدام الصوت المحلي."""

        text = text.strip()
        if not text:
            return

        subprocess.run(
            ["say", "-v", self.voice, text],
            check=True,
        )
