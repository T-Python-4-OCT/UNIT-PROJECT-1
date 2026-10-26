import json
import os

DB_FILE = "cyber_cases.json"

def load_cases():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_cases(cases):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False