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
