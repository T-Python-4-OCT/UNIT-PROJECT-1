import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _path(name):
    return os.path.join(DATA_DIR, f"{name}.json")


def load(name, default=None):
    """Load data/<name>.json. Returns `default` (or []) if missing/corrupt."""
    fallback = [] if default is None else default
    path = _path(name)
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return fallback


def save(name, data):
    """Save data safely (write to a temp file, then replace)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = _path(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, _path(name))