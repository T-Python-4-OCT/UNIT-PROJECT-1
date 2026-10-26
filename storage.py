import json
import os
from dataclasses import asdict

from models import Reservation, Table

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TABLES_FILE = os.path.join(DATA_DIR, "tables.json")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.json")

DEFAULT_TABLES = [
    Table(1, 2, "indoor"),
    Table(2, 3, "indoor"),
    Table(3, 4, "indoor"),
    Table(4, 4, "outdoor"),
    Table(5, 6, "family"),
    Table(6, 8, "family"),
]

def _read(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {os.path.basename(path)} is corrupted, using empty data.")
        return None


def _write(path, items):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(i) for i in items], f, indent=2, ensure_ascii=False)



def load_tables():
    data = _read(TABLES_FILE)
    if data is None:
        save_tables(DEFAULT_TABLES)
        return list(DEFAULT_TABLES)
    return [Table(**d) for d in data]


def save_tables(tables):
    _write(TABLES_FILE, tables)


def load_reservations():
    data = _read(RESERVATIONS_FILE) or []
    return [Reservation(**d) for d in data]


def save_reservations(reservations):
    _write(RESERVATIONS_FILE, reservations)
