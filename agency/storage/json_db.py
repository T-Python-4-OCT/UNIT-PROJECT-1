import json
import os
from pathlib import Path

from agency.errors import ServiceError


# تقرأ ملف JSON، وترجع قائمة فاضية إذا ما وجد.
def load(path: Path) -> list:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        raise ServiceError(f"Data file is corrupted: {path.name}")


# تحفظ القائمة في ملف JSON (بملف مؤقت أول عشان ما يخرب الملف).
def save(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


# ترجع الرقم التالي (أكبر رقم موجود + 1).
def next_id(items: list) -> int:
    return max((item["id"] for item in items), default=0) + 1
