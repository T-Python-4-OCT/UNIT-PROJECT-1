from interface.arabic_text import ArabicText
from interface.arabic_text import print_arabic

import threading
import time
import urllib.request
from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parents[1]
AUDIO_CACHE = BASE_DIR / "data" / "audio_cache"

AUDIO_BASE_URL = (
    "https://everyayah.com/data/"
    "Alafasy_128kbps"
)


class AudioPlayer:
    """مشغل تلاوة القرآن الكريم بصوت مشاري العفاسي."""

    def __init__(self):
        AUDIO_CACHE.mkdir(parents=True, exist_ok=True)

        pygame.mixer.init()

        self.stop_event = threading.Event()
        self.worker = None
        self.lock = threading.Lock()

    def _get_audio_file(self, surah_number, ayah_number):
        """تنزيل ملف الآية إذا لم يكن موجودًا في الذاكرة المؤقتة."""

        filename = f"{surah_number:03d}{ayah_number:03d}.mp3"
        file_path = AUDIO_CACHE / filename

        if file_path.exists() and file_path.stat().st_size > 0:
            return file_path

        url = f"{AUDIO_BASE_URL}/{filename}"
        temporary_path = file_path.with_suffix(".tmp")

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Taysir-Quran-CLI/1.0"},
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if "text/html" in content_type:
                    raise ValueError(
                        "المصدر أعاد صفحة ويب بدل ملف صوتي."
                    )

                with temporary_path.open("wb") as audio_file:
                    while True:
                        chunk = response.read(64 * 1024)

                        if not chunk:
                            break

                        audio_file.write(chunk)

            if not temporary_path.exists() or temporary_path.stat().st_size == 0:
                raise ValueError("ملف الصوت فارغ.")

            temporary_path.replace(file_path)
            return file_path

        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

    def _play_one(self, surah_number, ayah_number):
        """تشغيل آية واحدة وانتظار انتهائها."""

        if self.stop_event.is_set():
            return

        audio_file = self._get_audio_file(
            surah_number,
            ayah_number,
        )

        if self.stop_event.is_set():
            return

        pygame.mixer.music.load(str(audio_file))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if self.stop_event.is_set():
                pygame.mixer.music.stop()
                return

            time.sleep(0.1)

    def _start(self, worker_function):
        """إيقاف المهمة السابقة وتشغيل مهمة جديدة في الخلفية."""

        self.stop()

        self.stop_event = threading.Event()
        event = self.stop_event

        def run():
            try:
                worker_function(event)
            except Exception as error:
                if not event.is_set():
                    print(f"\nتعذّر تشغيل التلاوة: {error}")
            finally:
                if not event.is_set():
                    print("\nانتهت التلاوة.")

        self.worker = threading.Thread(
            target=run,
            daemon=True,
        )
        self.worker.start()

    def play_ayah(self, surah_number, ayah_number, repeats=3):
        """تشغيل الآية وتكرارها العدد المحدد من المرات."""

        if repeats < 1:
            raise ValueError("عدد مرات التكرار يجب أن يكون واحدًا على الأقل.")

        def task(event):
            print_arabic(
                f"جارٍ تشغيل الآية {ayah_number} "
                f"من السورة {surah_number}، "
                f"عدد التكرارات: {repeats}."
            )

            for _ in range(repeats):
                if event.is_set():
                    break

                self._play_one(surah_number, ayah_number)

        self._start(task)

    def play_surah(self, ayahs):
        """تشغيل جميع آيات السورة بالتتابع مرة واحدة."""

        if not ayahs:
            print("لا توجد آيات لتشغيلها.")
            return

        def task(event):
            first = ayahs[0]

            print(
                f"\nجارٍ تشغيل سورة {first['surah_name']} "
                "بصوت مشاري العفاسي."
            )

            for ayah in ayahs:
                if event.is_set():
                    break

                self._play_one(
                    ayah["surah_number"],
                    ayah["ayah_number"],
                )

        self._start(task)

    def stop(self):
        """إيقاف التلاوة الحالية."""

        old_event = self.stop_event
        old_event.set()

        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

        if (
            self.worker is not None
            and self.worker.is_alive()
            and self.worker is not threading.current_thread()
        ):
            self.worker.join(timeout=1)

        print_arabic("تم إيقاف التلاوة.")

    def close(self):
        """إيقاف الصوت وإغلاق مشغل الصوت."""

        self.stop()

        if pygame.mixer.get_init():
            pygame.mixer.quit()
