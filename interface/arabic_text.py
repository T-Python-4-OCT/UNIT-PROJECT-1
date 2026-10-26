import arabic_reshaper
from bidi.algorithm import get_display
from rich.console import Console
from rich.text import Text


def ArabicText(text=""):
    """تهيئة النص العربي للعرض في الطرفية."""
    return get_display(arabic_reshaper.reshape(str(text)))


def print_arabic(text="", console=None, **kwargs):
    """عرض النص العربي بعد تهيئته لاتجاه الطرفية."""
    if console is None:
        console = Console()

    console.print(
        Text(ArabicText(text), justify="right"),
        **kwargs
    )
