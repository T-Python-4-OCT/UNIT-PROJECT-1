"""Saving and loading (Lesson 7: files and folders, Lesson 8: try/except/else/finally)."""
import json
from datetime import datetime
from pathlib import Path

from .models import StorageError, Trip, TripError

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "trip.json"
REPORTS_DIR = ROOT / "reports"


def save_trip(trip: Trip) -> None:
    DATA_FILE.parent.mkdir(exist_ok=True)
    try:
        DATA_FILE.write_text(json.dumps(trip.to_dict(), indent=2, ensure_ascii=False),
                             encoding="utf-8")
    except OSError as err:
        raise StorageError(f"Could not save your data: {err}") from err


def load_trip() -> Trip | None:
    """Return the saved trip, or None on the first run."""
    if not DATA_FILE.exists():
        return None
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        trip = Trip.from_dict(data)
    except (OSError, ValueError, KeyError, TypeError, TripError) as err:
        raise StorageError(f"{DATA_FILE.name} is damaged ({err}). "
                           "Fix or delete the file and run again.") from err
    else:
        return trip
    finally:
        pass  # nothing to close: read_text() already closed the file


def delete_saved_trip() -> None:
    DATA_FILE.unlink(missing_ok=True)


def save_report(text: str, destination: str) -> Path:
    """Write the report to reports/<destination>_<date-time>.txt"""
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = "".join(ch for ch in destination if ch.isalnum()) or "trip"
    path = REPORTS_DIR / f"{name}_{stamp}.txt"
    number = 2
    while path.exists():  # two reports in the same second: don't overwrite
        path = REPORTS_DIR / f"{name}_{stamp}_{number}.txt"
        number += 1
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as err:
        raise StorageError(f"Could not save the report: {err}") from err
    return path.relative_to(ROOT)  # e.g. reports/Istanbul_20261022_120000.txt
