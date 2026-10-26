
"""تحويل النص إلى صوت macOS متوافق مع LiveKit."""

import asyncio
import subprocess
import tempfile
import uuid
import wave
from pathlib import Path

from livekit.agents import tts


class MacLiveKitTTS(tts.TTS):
    """استخدام صوت Majed المحلي لإنتاج صوت المساعد."""

    def __init__(self, voice: str = "Majed"):
        super().__init__(
            capabilities=tts.TTSCapabilities(
                streaming=False,
                aligned_transcript=False,
            ),
            sample_rate=24000,
            num_channels=1,
        )
        self.voice = voice

    def synthesize(
        self,
        text: str,
        *,
        conn_options,
    ) -> tts.ChunkedStream:
        return _MacChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options,
        )


class _MacChunkedStream(tts.ChunkedStream):
    async def _run(self, output_emitter) -> None:
        text = self._input_text.strip()

        if not text:
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "speech.wav"

            process = await asyncio.create_subprocess_exec(
                "say",
                "-v",
                self._tts.voice,
                "-o",
                str(audio_path),
                "--data-format=LEI16@24000",
                text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(
                    "فشل توليد الصوت بواسطة macOS: "
                    + stderr.decode("utf-8", errors="replace")
                )

            with wave.open(str(audio_path), "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                pcm_data = wav_file.readframes(
                    wav_file.getnframes()
                )

        if not pcm_data:
            raise RuntimeError("ملف الصوت الناتج فارغ.")

        if sample_width != 2:
            raise RuntimeError(
                f"عمق الصوت غير مدعوم: {sample_width * 8} بت."
            )

        if sample_rate != 24000 or channels != 1:
            raise RuntimeError(
                "إعدادات الصوت غير متوافقة مع LiveKit: "
                f"{sample_rate} Hz، {channels} قناة."
            )

        output_emitter.initialize(
            request_id=str(uuid.uuid4()),
            sample_rate=sample_rate,
            num_channels=channels,
            mime_type="audio/pcm",
        )

        # إرسال الصوت على دفعات صغيرة.
        bytes_per_sample = sample_width * channels
        chunk_size = 1200 * bytes_per_sample

        for start in range(0, len(pcm_data), chunk_size):
            chunk = pcm_data[start:start + chunk_size]

            if not chunk:
                continue

            output_emitter.push(chunk)

        output_emitter.flush()
