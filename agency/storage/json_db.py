"""Tiny JSON file storage: load, save and next id (the users file is stored encrypted)."""
import json
import os
from pathlib import Path

from agency.config import USERS_FILE
from agency.errors import ServiceError
from agency.utils import secure

ENCRYPTED_FILES = {USERS_FILE}      # personal data: names, emails, phones and password hashes


# تقرأ ملف JSON، وترجع قائمة فاضية إذا ما وجد.
def load(path: Path) -> list:
    """Read a JSON list from disk. Missing or empty file -> empty list."""
    if not path.exists() or path.stat().st_size == 0:
        return []
    raw = path.read_bytes()
    try:
        # An old plain-text users file still loads; it is encrypted the next time it is saved.
        if path in ENCRYPTED_FILES and not raw.lstrip().startswith((b"[", b"{")):
            return json.loads(secure.decrypt(raw))
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ServiceError(f"Data file is corrupted: {path.name}")


# تحفظ القائمة في ملف JSON (بملف مؤقت أول عشان ما يخرب الملف).
def save(path: Path, data: list) -> None:
    """Write safely: write to a temp file first, then replace the original."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    text = json.dumps(data, ensure_ascii=False, indent=2)
    content = secure.encrypt(text) if path in ENCRYPTED_FILES else text.encode("utf-8")
    with open(tmp, "wb") as handle:
        handle.write(content)
    os.replace(tmp, path)


# ترجع الرقم التالي (أكبر رقم موجود + 1).
def next_id(items: list) -> int:
    """Next free numeric id for a list of dicts."""
    return max((item["id"] for item in items), default=0) + 1
