"""Data storage module for reading and writing JSON files in StudyMate."""

import os
import json

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "study_mate.json")


def load_data():
    """Load data from JSON file or create an empty structure if it doesn't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(DATA_FILE):
        empty_data = {"subjects": [], "tasks": [], "exams": [], "notes": []}
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(empty_data, file, indent=4, ensure_ascii=False)
        return empty_data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {"subjects": [], "tasks": [], "exams": [], "notes": []}


def save_data(data):
    """Save the application data dictionary to the JSON file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)