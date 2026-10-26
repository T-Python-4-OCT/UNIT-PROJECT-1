
from voice.arabic_pronunciation import prepare_arabic_for_tts

tests = [
    "استمع إلى السور التالية في القرآن",
    "سور القرآن كثيرة",
    "تكتب الي في المحادثة",
]

for original in tests:
    prepared = prepare_arabic_for_tts(original)
    print("الأصل: ", original)
    print("للصوت:", prepared)
    print("-" * 30)
