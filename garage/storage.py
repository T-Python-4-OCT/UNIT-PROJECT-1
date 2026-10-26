"""Reading and writing JSON files (the "database" of the garage)."""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


class StorageError(Exception):
    """Raised when a data file cannot be read, parsed or written."""


class JsonStorage:
    """Safe read/write access to a single JSON file.

    Writes are atomic: the data goes to a temporary file first and then
    replaces the real file, so a crash can never leave a half-written file.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self, default: Any = None) -> Any:
        """Return the parsed JSON, or ``default`` if the file is missing/empty."""
        if not self.path.exists():
            return default
        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Cannot read {self.path.name}: {exc}") from exc
        if not text.strip():
            return default
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise StorageError(
                f"{self.path.name} is corrupted ({exc.msg}, line {exc.lineno})."
            ) from exc

    def write(self, data: Any) -> None:
        """Atomically write ``data`` as pretty JSON (Arabic text stays readable)."""
        tmp_name: str | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(
                dir=self.path.parent, prefix=f"{self.path.name}.", suffix=".tmp"
            )
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_name, self.path)
            tmp_name = None
        except (OSError, TypeError, ValueError) as exc:
            raise StorageError(f"Cannot write {self.path.name}: {exc}") from exc
        finally:
            if tmp_name is not None:
                Path(tmp_name).unlink(missing_ok=True)

    def backup_corrupted(self) -> Path | None:
        """Move a corrupted file aside (``*.corrupt``) and return the new path."""
        if not self.path.exists():
            return None
        backup = self.path.with_name(self.path.name + ".corrupt")
        if backup.exists():
            backup = self.path.with_name(f"{self.path.name}.{int(time.time())}.corrupt")
        try:
            self.path.replace(backup)
        except OSError as exc:
            raise StorageError(f"Cannot back up {self.path.name}: {exc}") from exc
        return backup


class VehicleStorage(JsonStorage):
    """JSON storage shaped like ``{"vehicles": [ {...}, {...} ]}``."""

    ROOT_KEY = "vehicles"

    def load_vehicles(self) -> list[dict[str, Any]]:
        data = self.read(default={self.ROOT_KEY: []})
        if not isinstance(data, dict) or not isinstance(data.get(self.ROOT_KEY), list):
            raise StorageError(
                f"{self.path.name} is corrupted (expected a '{self.ROOT_KEY}' list)."
            )
        return data[self.ROOT_KEY]

    def save_vehicles(self, vehicles: list[dict[str, Any]]) -> None:
        self.write({self.ROOT_KEY: vehicles})
