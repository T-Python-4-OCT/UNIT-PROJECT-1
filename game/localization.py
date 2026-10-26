# تبديل اللغة العربية والإنجليزية



import json
import arabic_reshaper

from pathlib import Path
from bidi.algorithm import get_display

TRANSLATIONS_FILE = (
    Path(__file__).parent / "data" / "translations.json"
)

DEFAULT_LANGUAGE = "ar"
SUPPORTED_LANGUAGES = ("ar", "en")


class Localization:
    def __init__(self, language=DEFAULT_LANGUAGE):
        self.translations = self.load_translations()
        self.set_language(language)

    def load_translations(self):
        try:
            with TRANSLATIONS_FILE.open(
                "r", encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("Invalid translations format.")

            return data

        except (OSError, json.JSONDecodeError, ValueError):
            return {}

    def set_language(self, language):
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE

        self.language = language

    def get_text(self, key, **kwargs):
        language_data = self.translations.get(
            self.language, {}
        )

        text = language_data.get(key)

        if text is None:
            text = self.translations.get(
                "en", {}
            ).get(key, key)

        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass

        return text

    def display_text(self, key, **kwargs):
        text = self.get_text(key, **kwargs)

        if self.language == "ar":
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)

        return text

    def format_arabic(self, text):
        if self.language == "ar":
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)

        return text