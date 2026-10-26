import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data")


def load_data(filename):
    file_path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(filename, data):
    file_path = os.path.join(DATA_FOLDER, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)