import arabic_reshaper
from bidi.algorithm import get_display


def ArabicText(text):
    """تهيئة النص العربي للعرض في الطرفية."""
    if not isinstance(text, str):
        text = str(text)

    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text, base_dir="R")
