import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_data(filename):
    """Read data from a JSON file."""
    file_path = DATA_DIR / filename

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return []


def save_data(filename, data):
    """Save data to a JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / filename

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return True
