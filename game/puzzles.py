# يحتوي الألغاز والإجابات والتلميحاتimport json


import json
import random
from pathlib import Path
import questionary
from game.localization import Localization
from game.scoring import Scoring


DATA_DIR = Path(__file__).parent / "data"
PUZZLES_FILE = DATA_DIR / "puzzles.json"
PUZZLES_AR_FILE = DATA_DIR / "puzzles_ar.json"

QUESTIONARY_STYLE = questionary.Style([
    ("pointer", "fg:#C5A46D bold"),
    ("highlighted", "fg:#A3B18A bold"),
    ("selected", "fg:#2F5249"),
    ("question", "fg:#C5A46D"),
])


def load_puzzles():
    with PUZZLES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_arabic_puzzles():
    with PUZZLES_AR_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def select_random_puzzles():
    puzzle_bank = load_puzzles()
    selected_puzzles = {}

    for puzzle_id, questions in puzzle_bank.items():
        selected_index = random.randrange(len(questions))
        selected_puzzle = questions[selected_index].copy()

        selected_puzzle["question_index"] = selected_index
        selected_puzzle["wrong_attempts"] = 0
        selected_puzzle["hint_used"] = False
        selected_puzzle["earned_points"] = 0

        selected_puzzles[puzzle_id] = selected_puzzle

    return selected_puzzles


def solve_puzzle(
    puzzle_id, selected_puzzles, journal=None, loc=None
):
    if loc is None:
        loc = Localization("en")

    puzzle_id = str(puzzle_id)
    puzzle = selected_puzzles.get(puzzle_id)

    if puzzle is None:
        message = (
            "خطأ: لم يتم العثور على اللغز."
            if loc.language == "ar"
            else f"Error: Puzzle '{puzzle_id}' not found."
        )
        print(loc.format_arabic(message))
        return False

    question = puzzle["question"]
    options = puzzle["options"]
    hint = puzzle["hint"]

    puzzle.setdefault("wrong_attempts", 0)
    puzzle.setdefault("hint_used", False)
    puzzle.setdefault("earned_points", 0)

    if loc.language == "ar":
        arabic_bank = load_arabic_puzzles()
        question_index = puzzle.get("question_index")

        if question_index is None:
            original_questions = load_puzzles().get(
                puzzle_id, []
            )

            for index, original in enumerate(original_questions):
                if original["question"] == puzzle["question"]:
                    question_index = index
                    break

        arabic_questions = arabic_bank.get(puzzle_id, [])

        if (
            question_index is not None
            and 0 <= question_index < len(arabic_questions)
        ):
            translated = arabic_questions[question_index]
            question = translated["question"]
            options = translated["options"]
            hint = translated["hint"]

    print(f"\n🔮 {loc.format_arabic(question)}\n")

    while True:
        answer_prompt = (
            "اختر إجابتك باستخدام الأسهم:"
            if loc.language == "ar"
            else "Choose your answer using the arrow keys:"
        )

        choices = [
            questionary.Choice(
                title=f"{index}. {loc.format_arabic(option)}",
                value=index,
            )
            for index, option in enumerate(options, start=1)
        ]

        if not puzzle["hint_used"]:
            hint_label = (
                "💡 عرض التلميح (-10 نقاط)"
                if loc.language == "ar"
                else "💡 Show Hint (-10 points)"
            )

            choices.append(
                questionary.Choice(
                    title=loc.format_arabic(hint_label),
                    value="hint",
                )
            )

        journal_label = (
            "📜 عرض دفتر الرحلة"
            if loc.language == "ar"
            else "📜 Review Journal"
        )

        choices.append(
            questionary.Choice(
                title=loc.format_arabic(journal_label),
                value="journal",
            )
        )

        answer = questionary.select(
            loc.format_arabic(answer_prompt),
            choices=choices,
            pointer="❯",
            style=QUESTIONARY_STYLE,
            use_shortcuts=False,
        ).ask()

        if answer is None:
            return False

        if answer == "journal":
            if journal is not None:
                journal.display()
            else:
                message = (
                    "دفتر الرحلة غير متاح."
                    if loc.language == "ar"
                    else "Journal is unavailable."
                )
                print(loc.format_arabic(message))

            continue

        if answer == "hint":
            puzzle["hint_used"] = True

            hint_label = (
                "💡 تلميح"
                if loc.language == "ar"
                else "💡 Hint"
            )

            print(
                f"\n{loc.format_arabic(hint_label)}: "
                f"{loc.format_arabic(hint)}"
            )

            continue

        if answer == puzzle["correct"]:
            earned_points = Scoring.calculate_puzzle_reward(
                wrong_attempts=puzzle["wrong_attempts"],
                hint_used=puzzle["hint_used"],
            )

            puzzle["earned_points"] = earned_points

            message = (
                "✨ إجابة صحيحة! تكشف الغابة أحد أسرارها."
                if loc.language == "ar"
                else "✨ Correct! The forest reveals its secret."
            )

            points_message = (
                f"🏆 نقاط اللغز: {earned_points}/100"
                if loc.language == "ar"
                else f"🏆 Puzzle Points: {earned_points}/100"
            )

            print(f"\n{loc.format_arabic(message)}")
            print(loc.format_arabic(points_message))

            return True

        puzzle["wrong_attempts"] += 1

        message = (
            "❌ إجابة خاطئة، حاول مجددًا. (-20 نقطة)"
            if loc.language == "ar"
            else "❌ Incorrect answer, try again. (-20 points)"
        )

        print(f"\n{loc.format_arabic(message)}")