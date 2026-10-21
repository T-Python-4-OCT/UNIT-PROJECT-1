
import json
import tempfile
import unittest
from pathlib import Path

from quran.quran_reader import QuranReader
from tafsir.tafsir_reader import TafsirReader


class TestQuranReader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "quran.json"

        self.ayahs = [
            {
                "surah_number": 1,
                "surah_name": "الفاتحة",
                "ayah_number": 1,
                "text": "بسم الله الرحمن الرحيم"
            },
            {
                "surah_number": 1,
                "surah_name": "الفاتحة",
                "ayah_number": 2,
                "text": "الحمد لله رب العالمين"
            }
        ]

        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(self.ayahs, file, ensure_ascii=False)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_ayahs(self):
        reader = QuranReader(self.file_path)
        self.assertEqual(len(reader.ayahs), 2)

    def test_find_ayah(self):
        reader = QuranReader(self.file_path)
        ayah = reader.find(1, 2)

        self.assertIsNotNone(ayah)
        self.assertEqual(ayah["ayah_number"], 2)

    def test_find_missing_ayah(self):
        reader = QuranReader(self.file_path)
        self.assertIsNone(reader.find(1, 99))

    def test_search(self):
        reader = QuranReader(self.file_path)
        results = reader.search("الحمد")

        self.assertEqual(len(results), 1)

    def test_empty_search(self):
        reader = QuranReader(self.file_path)
        self.assertEqual(reader.search(""), [])

    def test_missing_file(self):
        missing_path = self.file_path.parent / "missing.json"
        reader = QuranReader(missing_path)

        self.assertEqual(reader.ayahs, [])


class TestTafsirReader(unittest.TestCase):

    def test_get_tafsir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "tafsir.json"

            data = [
                {
                    "surah_number": 1,
                    "ayah_number": 1,
                    "text": "نص تفسيري للاختبار فقط"
                }
            ]

            with file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False)

            reader = TafsirReader(file_path)

            self.assertEqual(
                reader.get(1, 1),
                "نص تفسيري للاختبار فقط"
            )

    def test_missing_tafsir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "tafsir.json"
            reader = TafsirReader(file_path)

            self.assertIsNone(reader.get(1, 1))


if __name__ == "__main__":
    unittest.main()
