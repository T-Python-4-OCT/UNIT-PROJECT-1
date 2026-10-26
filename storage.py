"""
storage.py
Loads and saves app data to a JSON file.
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = os.getenv("DATA_FILE", "unimate_data.json")
DATA_KEYS = ["users", "subjects", "tasks", "projects", "exams", "notes"]


def load_data():
    # Load data from JSON, or return empty lists if the file does not exist
    default_data = {key: [] for key in DATA_KEYS}
    if not os.path.exists(DATA_FILE):
        return default_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            for key in default_data:
                if key not in data:
                    data[key] = []
            return data
    except Exception:
        return default_data


def save_data(data):
    # Convert objects to dictionaries and write them to the JSON file
    try:
        serializable_data = {}
        for key in DATA_KEYS:
            serializable_data[key] = [
                item.to_dict() if hasattr(item, "to_dict") else item
                for item in data.get(key, [])
            ]
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(serializable_data, file, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False