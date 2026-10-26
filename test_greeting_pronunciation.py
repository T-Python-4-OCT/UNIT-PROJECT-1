from voice.najdi_tts import NajdiTTS
from voice.arabic_pronunciation import prepare_arabic_for_tts

tts = NajdiTTS()

tests = [
    "السور التالية",
    "الإنْتِقَال بين الآيات والسور",
    "والانتقال بين الآيات والسور",
    (
        "أستطيع مساعدتك في قراءة القرآن الكريم، "
        "والانتقال بين الآيات والسور، "
        "وعرض التفسير الميسّر، والبحث في القرآن، "
        "وتشغيل التلاوة الصوتية."
    ),
]

for index, sentence in enumerate(tests, start=1):
    prepared = prepare_arabic_for_tts(sentence)

    print(f"\nالاختبار {index}")
    print("النص المجهز:", prepared)

    input("اضغط Enter لسماع الجملة...")
    tts.speak(sentence)
