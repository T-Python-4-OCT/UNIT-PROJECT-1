from voice.najdi_tts import NajdiTTS

tts = NajdiTTS()

tests = [
    "السور",
    "السور التالية",
    "التحدث إلي",
    "والانتقال بين الآيات والسور التالية",
]

for text in tests:
    print("\nالنص:", text)
    input("اضغط Enter لسماع النطق...")
    tts.speak(text)
