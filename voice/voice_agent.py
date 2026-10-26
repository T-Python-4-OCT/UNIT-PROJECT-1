"""نظام التعرف الصوتي الهجين لتطبيق تيسير: محلي أولًا ثم Gemini."""

import os
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from faster_whisper import WhisperModel


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BASE_DIR / ".env")


class VoiceAgent:
    """التعرف على الكلام محليًا مع رجوع سحابي عند الحاجة."""

    def __init__(
        self,
        model_size=None,
        sample_rate=16000,
        recording_seconds=6,
    ):
        self.model_size = (
            model_size
            or os.getenv("TAYSIR_LOCAL_ASR_MODEL", "small")
        )
        self.sample_rate = sample_rate
        self.recording_seconds = recording_seconds
        self.model = None

        self.cloud_enabled = (
            os.getenv("TAYSIR_CLOUD_ASR", "true").lower()
            in {"1", "true", "yes", "on"}
        )

        self.min_logprob = float(
            os.getenv("TAYSIR_ASR_MIN_LOGPROB", "-0.65")
        )

        self.max_no_speech = float(
            os.getenv("TAYSIR_ASR_MAX_NO_SPEECH", "0.60")
        )

    @staticmethod
    def _print_arabic(message):
        print(str(message))

    def _load_model(self):
        """تحميل Whisper عند أول استخدام، ثم إعادة استخدامه."""

        if self.model is None:
            self._print_arabic(
                "جارٍ تحميل نموذج التعرف الصوتي المحلي..."
            )

            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
            )

            self._print_arabic(
                "تم تحميل نموذج Whisper المحلي."
            )

    def record_audio(self):
        """تسجيل الصوت مرة واحدة وإرجاع مصفوفة صوتية."""

        self._print_arabic(
            f"تحدث الآن باللغة العربية لمدة "
            f"{self.recording_seconds} ثوانٍ..."
        )

        audio = sd.rec(
            int(self.recording_seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )

        sd.wait()

        audio = np.asarray(
            audio,
            dtype=np.float32,
        ).reshape(-1)

        if audio.size == 0:
            raise RuntimeError("لم يتم تسجيل أي صوت.")

        if not np.isfinite(audio).all():
            raise RuntimeError("التسجيل يحتوي على قيم صوتية غير صالحة.")

        if float(np.max(np.abs(audio))) < 0.003:
            raise RuntimeError(
                "الصوت منخفض جدًا أو لم يُسجّل. تحقق من الميكروفون."
            )

        return audio

    def _transcribe_local(self, audio):
        """
        يعيد النص المحلي ومتوسط avg_logprob ومتوسط no_speech_prob.
        تمرير مصفوفة NumPy مباشرة يتجنب فتح ملف صوتي بواسطة PyAV.
        """

        self._load_model()

        audio = np.asarray(
            audio,
            dtype=np.float32,
        ).reshape(-1)

        segments, _ = self.model.transcribe(
            audio,
            language="ar",
            beam_size=3,
            vad_filter=False,
            condition_on_previous_text=False,
        )

        # استهلاك المولد حتى نحصل على كل المقاطع وبيانات الثقة.
        segments = list(segments)

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        if not segments:
            return "", -1.0, 1.0

        avg_logprob = sum(
            float(segment.avg_logprob)
            for segment in segments
        ) / len(segments)

        no_speech_prob = sum(
            float(segment.no_speech_prob)
            for segment in segments
        ) / len(segments)

        return text, avg_logprob, no_speech_prob

    def transcribe(self, audio):
        """واجهة التوافق القديمة: تعيد النص المحلي فقط."""

        text, _, _ = self._transcribe_local(audio)
        return text

    def _needs_cloud_fallback(
        self,
        text,
        avg_logprob,
        no_speech_prob,
    ):
        """تحديد ما إذا كانت هناك مؤشرات تستدعي المحاولة السحابية."""

        if not text or not text.strip():
            return True

        if len(text.strip()) < 3:
            return True

        if avg_logprob < self.min_logprob:
            return True

        if no_speech_prob > self.max_no_speech:
            return True

        return False

    def _transcribe_cloud(self, audio):
        """إرسال التسجيل إلى Gemini للتفريغ الصوتي ثم حذف الملف السحابي."""

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "مفتاح GEMINI_API_KEY غير موجود في ملف .env."
            )

        # استيراد العميل عند الحاجة فقط؛ يبقى التشغيل المحلي مستقلًا.
        from google import genai

        client = genai.Client(api_key=api_key)
        model_name = os.getenv(
            "GEMINI_ASR_MODEL",
            "gemini-3.5-transcribe",
        )

        temporary_path = None
        uploaded_file = None

        try:
            # تحويل المصفوفة إلى WAV أحادي القناة بتنسيق PCM 16-bit.
            pcm_audio = (
                np.clip(audio, -1.0, 1.0) * 32767
            ).astype("<i2")

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                prefix="taysir_asr_",
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name

            with wave.open(temporary_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(pcm_audio.tobytes())

            self._print_arabic(
                "النص المحلي يحتاج إلى مراجعة؛ "
                "جارٍ تجربة التفريغ الصوتي عبر Gemini..."
            )

            uploaded_file = client.files.upload(
                file=temporary_path
            )

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    uploaded_file,
                    (
                        "Transcribe the spoken audio accurately. "
                        "The expected language is Arabic. "
                        "Return only the spoken words, without "
                        "translation, explanation, or invented text."
                    ),
                ],
            )

            text = (getattr(response, "text", "") or "").strip()

            if not text:
                raise RuntimeError(
                    "لم تُرجع خدمة Gemini نصًا للتسجيل."
                )

            return text

        finally:
            # حذف النسخة المحلية المؤقتة.
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)

            # محاولة حذف الملف المرفوع بعد انتهاء المعالجة.
            if uploaded_file is not None:
                try:
                    client.files.delete(name=uploaded_file.name)
                except Exception as error:
                    self._print_arabic(
                        "تنبيه: تعذر حذف الملف الصوتي من خدمة Gemini: "
                        f"{error}"
                    )

            try:
                client.close()
            except Exception:
                pass

    def listen(self):
        """
        تسجيل واحد، ثم Whisper محليًا، ثم Gemini عند الحاجة.
        إذا فشل الرجوع السحابي، تُستخدم النتيجة المحلية إن توفرت.
        """

        try:
            audio = self.record_audio()
        except Exception as error:
            self._print_arabic(
                f"تعذر تسجيل الصوت: {error}"
            )
            return ""

        local_text = ""
        local_error = None
        avg_logprob = -1.0
        no_speech_prob = 1.0

        self._print_arabic(
            "جارٍ تحويل الكلام إلى نص محليًا..."
        )

        try:
            (
                local_text,
                avg_logprob,
                no_speech_prob,
            ) = self._transcribe_local(audio)

            if local_text:
                self._print_arabic(
                    f"نتيجة Whisper المحلية: {local_text}"
                )
                self._print_arabic(
                    "مؤشرات الثقة: "
                    f"avg_logprob={avg_logprob:.2f}, "
                    f"no_speech_prob={no_speech_prob:.2f}"
                )

        except Exception as error:
            local_error = error
            self._print_arabic(
                f"تعذر التفريغ المحلي: {error}"
            )

        needs_fallback = (
            local_error is not None
            or self._needs_cloud_fallback(
                local_text,
                avg_logprob,
                no_speech_prob,
            )
        )

        api_key_exists = bool(
            os.getenv("GEMINI_API_KEY")
        )

        if (
            needs_fallback
            and self.cloud_enabled
            and api_key_exists
        ):
            try:
                cloud_text = self._transcribe_cloud(audio)

                if cloud_text:
                    self._print_arabic(
                        "تم التعرف على الكلام باستخدام Gemini:"
                    )
                    self._print_arabic(cloud_text)
                    return cloud_text

            except Exception as error:
                self._print_arabic(
                    "تعذر التفريغ السحابي؛ "
                    f"سيحاول تيسير استخدام النتيجة المحلية: {error}"
                )

        elif needs_fallback and self.cloud_enabled:
            self._print_arabic(
                "لا يوجد مفتاح Gemini صالح؛ "
                "سيحاول تيسير استخدام النتيجة المحلية."
            )

        if local_text:
            self._print_arabic(
                "سيتم استخدام النص المحلي."
            )
            return local_text

        if local_error is not None:
            self._print_arabic(
                "لم ينجح التعرف المحلي، ولم تتوفر نتيجة سحابية."
            )

        else:
            self._print_arabic(
                "لم أتمكن من فهم الكلام. حاول مرة أخرى."
            )

        return ""

    def speak(self, text):
        """قراءة الرد باستخدام صوت macOS."""

        if not text:
            return

        try:
            subprocess.run(
                ["say", str(text)],
                check=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as error:
            self._print_arabic(
                f"تعذر تشغيل الرد الصوتي: {error}"
            )

    def run_once(self):
        """تسجيل مرة واحدة وعرض النص الناتج."""

        text = self.listen()

        if text:
            self._print_arabic(f"أنت قلت: {text}")

        return text
