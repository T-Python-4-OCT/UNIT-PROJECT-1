import json
import os
import tempfile


def load_json(file_path: str, default=None):
    """Read a JSON file. A missing file gives `default` ([] unless told otherwise).

    A corrupt file is renamed to '<file>.corrupt' (not silently replaced by an
    empty list that the next save would write over your data).
    """
    default = [] if default is None else default
    if not os.path.exists(file_path):
        return default
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            pass
    os.replace(file_path, file_path + ".corrupt")
    return default


def save_json(file_path: str, data):
    """Write atomically: dump to a temp file in the same folder, then swap it in,
    so a crash mid-write can't leave a half-written (broken) JSON file."""
    folder = os.path.dirname(file_path) or "."
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        os.replace(tmp, file_path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise