# يحدد النهاية حسب إنجازات اللاعب
import json
from pathlib import Path

from game.localization import Localization


ENDINGS_FILE = Path(__file__).parent / "data" / "endings.json"
ENDINGS_AR_FILE = Path(__file__).parent / "data" / "endings_ar.json"
PASSING_SCORE = 600


def load_endings():
    with ENDINGS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def determine_fate(
    scoring,
    journal=None,
    previous_choices=None,
    selected_puzzles=None,
):
    total = scoring.get_total()
    scores = scoring.scores

    discoveries = set(journal.discoveries) if journal else set()
    choices = previous_choices or {}
    puzzles = selected_puzzles or {}

    correct_puzzles = (
        len(journal.solved_puzzles)
        if journal
        else sum(
            1 for puzzle in puzzles.values()
            if puzzle.get("earned_points", 0) > 0
        )
    )

    positive = total >= PASSING_SCORE

    if positive:
        if (
            total >= 800
            and correct_puzzles >= 3
            and len(discoveries) >= 2
        ):
            return "golden_awakening"

        if (
            "forest_memory" in discoveries
            and scores.get("secrets", 0) >= 100
        ):
            return "forest_keeper"

        return "way_beyond"

    if scores.get("puzzles", 0) < 150:
        return "forgotten_soul"

    if (
        scores.get("decisions", 0) < 80
        or choices.get(2) == 2
    ):
        return "roots_of_eternity"

    return "eternal_wanderer"


def get_fate_title(fate_id, loc=None):
    if loc is None:
        loc = Localization("en")

    file_path = (
        ENDINGS_AR_FILE
        if loc.language == "ar"
        else ENDINGS_FILE
    )

    with file_path.open("r", encoding="utf-8") as file:
        endings = json.load(file)

    for category in endings.values():
        if fate_id in category:
            return category[fate_id]["title"]

    return fate_id


def display_ending(fate_id, loc=None):
    if loc is None:
        loc = Localization("en")

    file_path = (
        ENDINGS_AR_FILE
        if loc.language == "ar"
        else ENDINGS_FILE
    )

    with file_path.open("r", encoding="utf-8") as file:
        endings = json.load(file)

    for category in endings.values():
        if fate_id in category:
            fate = category[fate_id]

            print("\n" + "=" * 50)
            print(loc.format_arabic(fate["title"]))
            print("=" * 50)

            print(
                f"\n{loc.format_arabic(fate['description'])}"
            )

            message = (
                "الغابة تتذكر رحلتك."
                if loc.language == "ar"
                else "The forest remembers your journey."
            )

            print(f"\n{loc.format_arabic(message)}")
            return

    message = (
        "مصير غير معروف."
        if loc.language == "ar"
        else "Unknown fate."
    )

    print(f"\n{loc.format_arabic(message)}")