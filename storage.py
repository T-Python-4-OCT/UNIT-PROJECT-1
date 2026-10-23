import json
import os

DATA_FILE = "studymate_data.json"

def load_data():
    default_data = {"subjects": [], "tasks": [], "exams": [], "notes": []}
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
    try:
        serializable_data = {
            "subjects": [s.to_dict() if hasattr(s, "to_dict") else s for s in data.get("subjects", [])],
            "tasks": [t.to_dict() if hasattr(t, "to_dict") else t for t in data.get("tasks", [])],
            "exams": [e.to_dict() if hasattr(e, "to_dict") else e for e in data.get("exams", [])],
            "notes": [n.to_dict() if hasattr(n, "to_dict") else n for n in data.get("notes", [])]
        }
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(serializable_data, file, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False