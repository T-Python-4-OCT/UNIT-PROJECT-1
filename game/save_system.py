# يحفظ تقدم اللاعب ويستعيده



# Handles saving, loading, and deleting game progress.

import json
from pathlib import Path

SAVE_DIRECTORY = Path(__file__).resolve().parent.parent / "saves"
SAVE_FILE = SAVE_DIRECTORY / "savegame.json"
SAVE_VERSION = 1


def save_game(game_state):
    SAVE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    data = {
        "version": SAVE_VERSION,
        "game_state": game_state,
    }

    temporary_file = SAVE_FILE.with_suffix(".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        temporary_file.replace(SAVE_FILE)
        print("\nGame saved successfully!")
        return True

    except (OSError, TypeError, ValueError) as error:
        print(f"\nCould not save game: {error}")
        return False


def load_game():
    if not SAVE_FILE.exists():
        print("\nNo saved game found.")
        return None

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Invalid save file structure.")

        if data.get("version") != SAVE_VERSION:
            raise ValueError("Unsupported save version.")

        state = data.get("game_state")

        if not isinstance(state, dict):
            raise ValueError("Invalid game state.")

        required_fields = {
            "explorer",
            "exploration",
            "journal",
            "scoring",
            "selected_puzzles",
            "previous_choices",
        }

        if not required_fields.issubset(state):
            raise ValueError("Saved game is missing required fields.")

        print("\nGame loaded successfully!")
        return state

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"\nCould not load game: {error}")
        return None


def delete_save():
    try:
        if SAVE_FILE.exists():
            SAVE_FILE.unlink()
            print("\nPrevious save deleted.")
        return True

    except OSError as error:
        print(f"\nCould not delete save: {error}")
        return False
