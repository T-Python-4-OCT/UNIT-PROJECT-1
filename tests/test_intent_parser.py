import unittest

from commands.intent_parser import IntentParser


class TestIntentParser(unittest.TestCase):

    def setUp(self):
        self.parser = IntentParser({
            1: "الفاتحة",
            2: "البقرة",
            67: "الملك",
        })

    def test_search(self):
        result = self.parser.parse("ابحث عن الحمد لله")
        self.assertEqual(result.action, "search")
        self.assertEqual(result.query, "الحمد لله")

    def test_next_ayah(self):
        result = self.parser.parse("الآية التالية")
        self.assertEqual(result.action, "next")

    def test_tafsir(self):
        result = self.parser.parse("اعرض التفسير")
        self.assertEqual(result.action, "tafsir")

    def test_goto_surah_and_ayah(self):
        result = self.parser.parse("انتقل إلى سورة الملك الآية 5")
        self.assertEqual(result.action, "goto")
        self.assertEqual(result.surah, 67)
        self.assertEqual(result.ayah, 5)

    def test_play_surah(self):
        result = self.parser.parse("شغل السورة")
        self.assertEqual(result.action, "play_surah")

    def test_stop(self):
        result = self.parser.parse("أوقف التلاوة")
        self.assertEqual(result.action, "stop")

    def test_unknown_command(self):
        result = self.parser.parse("كيف حالك اليوم")
        self.assertEqual(result.action, "unknown")

    def test_empty_command(self):
        result = self.parser.parse("")
        self.assertEqual(result.action, "unknown")


if __name__ == "__main__":
    unittest.main()
