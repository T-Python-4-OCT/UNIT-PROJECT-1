import json
import os
import shutil
from datetime import datetime

from .errors import KickoffError
from .models import Booking, Match, Team

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
SEED = os.path.join(DATA, "seed")
TICKETS = os.path.join(BASE, "tickets")
LOG_FILE = os.path.join(DATA, "activity.log")
HOLDS_FILE = os.path.join(DATA, "holds.json")
FILES = ("teams.json", "matches.json", "bookings.json")


def ensure_data() -> None:
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(TICKETS, exist_ok=True)
    for name in FILES:
        target = os.path.join(DATA, name)
        if not os.path.exists(target):
            shutil.copy(os.path.join(SEED, name), target)


def _read(name: str):
    path = os.path.join(DATA, name)
    f = None
    try:
        f = open(path, encoding="utf-8")
        data = json.load(f)
    except FileNotFoundError:
        raise KickoffError(f"Data file {name} is missing.")
    except json.JSONDecodeError:
        raise KickoffError(f"Data file {name} is damaged. Delete it and run the app again.")
    else:
        return data
    finally:
        if f is not None:
            f.close()


def _write(name: str, data) -> None:
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_teams() -> dict[str, Team]:
    return {d["team_id"]: Team.from_dict(d) for d in _read("teams.json")}


def load_matches() -> list[Match]:
    return [Match.from_dict(d) for d in _read("matches.json")]


def load_bookings() -> list[Booking]:
    return [Booking.from_dict(d) for d in _read("bookings.json")]


def save_bookings(bookings: list[Booking]) -> None:
    _write("bookings.json", [b.to_dict() for b in bookings])


def next_booking_id(bookings: list[Booking]) -> str:
    numbers = [int(b.id.split("-")[1]) for b in bookings]
    return f"KT-{max(numbers, default=0) + 1:04d}"


def ticket_path(booking_id: str) -> str:
    return os.path.join(TICKETS, f"{booking_id}.txt")


def save_ticket_file(booking_id: str, text: str) -> str:
    path = ticket_path(booking_id)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def read_ticket_file(booking_id: str) -> str:
    path = ticket_path(booking_id)
    if not os.path.exists(path):
        raise KickoffError("No e-ticket file was found for this booking.")
    with open(path, encoding="utf-8") as f:
        return f.read()


def list_ticket_files() -> list[str]:
    return sorted(name for name in os.listdir(TICKETS) if name.endswith(".txt"))


def log(message: str) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {message}\n")