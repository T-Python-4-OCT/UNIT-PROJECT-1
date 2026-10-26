
"""تكامل Munsit مع واجهة STT في LiveKit."""

import asyncio
import io
import os
import uuid
import wave

import numpy as np
import requests
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import stt
from livekit.agents.utils import AudioBuffer
from livekit.agents.types import APIConnectOptions, NOT_GIVEN, NotGivenOr


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

MUNSIT_API_URL = "https://api.munsit.com/api/v1/audio/transcribe"


class LiveKitMunsitSTT(stt.STT):
    """إرسال الصوت إلى Munsit وإرجاع النص العربي إلى LiveKit."""

    def __init__(self):
        super().__init__(
            capabilities=stt.STTCapabilities(
                streaming=False,
                interim_results=False,
            )
        )

        self.api_key = os.getenv("MUNSIT_API_KEY", "").strip()

        if not self.api_key:
            raise RuntimeError(
                "لم يتم العثور على MUNSIT_API_KEY في ملف .env."
            )

    def _recognize_wav(self, audio_bytes: bytes) -> str:
        headers = {"x-api-key": self.api_key}
        files = {
            "file": ("speech.wav", audio_bytes, "audio/wav")
        }

        response = requests.post(
            MUNSIT_API_URL,
            headers=headers,
            files=files,
            data={"model": "munsit"},
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        data = result.get("data", {})
        transcript = data.get("transcription", "")

        if not isinstance(transcript, str) or not transcript.strip():
            raise RuntimeError("لم تُرجع Munsit نصًا صالحًا.")

        return transcript.strip()

    async def _recognize_impl(
        self,
        buffer: AudioBuffer,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions,
    ) -> stt.SpeechEvent:
        """تحويل الصوت المسجل إلى حدث تعرف على الكلام."""

        audio_frames = (
            [buffer] if isinstance(buffer, rtc.AudioFrame)
            else list(buffer)
        )

        if not audio_frames:
            raise RuntimeError("لم تصل أي إطارات صوتية إلى Munsit.")

        sample_rate = audio_frames[0].sample_rate
        num_channels = audio_frames[0].num_channels

        if any(
            frame.sample_rate != sample_rate
            or frame.num_channels != num_channels
            for frame in audio_frames
        ):
            raise RuntimeError(
                "تغيّر معدل العينة أو عدد القنوات داخل المقطع الصوتي."
            )

        pcm_parts = [
            np.frombuffer(frame.data, dtype=np.int16)
            for frame in audio_frames
        ]
        pcm = np.concatenate(pcm_parts)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm.tobytes())

        transcript = await asyncio.to_thread(
            self._recognize_wav,
            wav_buffer.getvalue(),
        )

        selected_language = (
            "ar" if language is NOT_GIVEN else str(language)
        )

        return stt.SpeechEvent(
            type=stt.SpeechEventType.FINAL_TRANSCRIPT,
            request_id=str(uuid.uuid4()),
            alternatives=[
                stt.SpeechData(
                    language=selected_language,
                    text=transcript,
                    confidence=0.0,
                )
            ],
        )
