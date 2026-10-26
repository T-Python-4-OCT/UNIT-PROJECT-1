# يحتوي القصة والأحداث التسعة


import json
import json
from pathlib import Path

STORY_AR_FILE = Path(__file__).parent / "data" / "story_ar.json"
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "story.json"


def load_story():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data["events"]


def localize_story(events, language):
    if language != "ar":
        return events

    with STORY_AR_FILE.open("r", encoding="utf-8") as file:
        arabic_events = json.load(file)["events"]

    translations = {
        event["id"]: event for event in arabic_events
    }

    for event in events:
        translated = translations.get(event["id"])

        if translated is None:
            continue

        event["title_ar"] = translated["title"]
        event["description_ar"] = translated["description"]

        for original, arabic in zip(
            event["choices"],
            translated["choices"]
        ):
            original["text_ar"] = arabic["text"]
            original["result_ar"] = arabic["result"]

    return events
