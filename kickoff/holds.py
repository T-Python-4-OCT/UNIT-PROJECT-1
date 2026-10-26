"""Temporary seat holds: a seat in someone's cart is held for a few minutes and shows yellow for everyone."""
import json
import os
from datetime import datetime, timedelta
from . import storage
from .errors import SeatHeldError

HOLD_MINUTES = 5
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _key(match_id, seat):
    return f"{match_id}:{seat}"


def _load():
    if not os.path.exists(storage.HOLDS_FILE):
        return {}
    try:
        with open(storage.HOLDS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return {}
    now = datetime.now()
    return {k: h for k, h in data.items() if datetime.strptime(h["until"], TIME_FORMAT) > now}


def _save(data):
    with open(storage.HOLDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def seconds_left(hold):
    return int((datetime.strptime(hold["until"], TIME_FORMAT) - datetime.now()).total_seconds())


def hold(match_id, seat, token):
    data = _load()
    current = data.get(_key(match_id, seat))
    if current and current["owner"] != token:
        minutes = max(1, seconds_left(current) // 60 + 1)
        raise SeatHeldError(f"{seat} is held by another fan for about {minutes} more minute(s).")
    until = datetime.now() + timedelta(minutes=HOLD_MINUTES)
    data[_key(match_id, seat)] = {"owner": token, "until": until.strftime(TIME_FORMAT)}
    _save(data)


def release(match_id, seat, token):
    data = _load()
    current = data.get(_key(match_id, seat))
    if current and current["owner"] == token:
        del data[_key(match_id, seat)]
    _save(data)


def release_all(token):
    data = _load()
    _save({k: h for k, h in data.items() if h["owner"] != token})


def seats_for(match_id, token):
    """Returns (mine, others): mine = {seat: seconds_left}, others = set of seats held by other fans."""
    mine, others = {}, set()
    for key, h in _load().items():
        mid, seat = key.split(":")
        if int(mid) != match_id:
            continue
        if h["owner"] == token:
            mine[seat] = seconds_left(h)
        else:
            others.add(seat)
    return mine, others