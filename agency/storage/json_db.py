"""Tiny JSON file storage: load, save and next id."""
import json
import os
from pathlib import Path

from agency.errors import ServiceError


def load(path: Path) -> list:
    """Read a JSON list from disk. Missing or empty file -> empty list."""
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        raise ServiceError(f"Data file is corrupted: {path.name}")


def save(path: Path, data: list) -> None:
    """Write safely: write to a temp file first, then replace the original."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def next_id(items: list) -> int:
    """Next free numeric id for a list of dicts."""
    return max((item["id"] for item in items), default=0) + 1
