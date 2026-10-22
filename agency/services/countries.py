import difflib

from agency.config import COUNTRIES_FILE
from agency.errors import ServiceError
from agency.models.country import Country
from agency.storage import json_db

CATEGORIES = ("city", "beach", "culture", "adventure")
_TEXT_FIELDS = ("country", "city", "best_season")
_INT_FIELDS = ("flight", "hotel", "food", "transport", "activities")


def _clean(data: dict) -> dict:
    out = dict(data)
    for field in _TEXT_FIELDS:
        value = str(out.get(field, "")).strip()
        if not value:
            raise ServiceError(f"'{field}' is required.")
        out[field] = value
    if out.get("category") not in CATEGORIES:
        raise ServiceError(f"Category must be one of: {', '.join(CATEGORIES)}.")
    for field in _INT_FIELDS:
        try:
            number = int(out[field])
        except (KeyError, TypeError, ValueError):
            raise ServiceError(f"'{field}' must be a whole number.")
        if number < 0:
            raise ServiceError(f"'{field}' cannot be negative.")
        out[field] = number
    highlights = out.get("highlights")
    if isinstance(highlights, str):
        highlights = [h.strip() for h in highlights.split(",") if h.strip()]
    if not highlights:
        raise ServiceError("At least one highlight is required.")
    out["highlights"] = list(highlights)
    return out


def list_all() -> list:
    return [Country.from_dict(record) for record in json_db.load(COUNTRIES_FILE)]


def get(country_id: int) -> Country:
    for destination in list_all():
        if destination.id == country_id:
            return destination
    raise ServiceError(f"No destination with ID {country_id}.")


def search(query: str = "", category: str = "") -> list:
    q = query.strip().lower()
    results = []
    for destination in list_all():
        if category and destination.category != category:
            continue
        if q and q not in f"{destination.country} {destination.city} {destination.category}".lower():
            continue
        results.append(destination)
    return results


def search_by(field: str, text: str):
    text = text.strip().lower()
    items = list_all()
    found = [item for item in items if text in getattr(item, field).lower()]
    if found or field == "category":
        return found, False
    close = difflib.get_close_matches(text, {getattr(item, field).lower() for item in items}, n=3, cutoff=0.6)
    return [item for item in items if getattr(item, field).lower() in close], bool(close)


def set_suspended(country_id: int, suspended: bool) -> Country:
    items = json_db.load(COUNTRIES_FILE)
    for raw in items:
        if raw["id"] == country_id:
            raw["suspended"] = suspended
            json_db.save(COUNTRIES_FILE, items)
            return Country.from_dict(raw)
    raise ServiceError(f"No destination with ID {country_id}.")


def add(data: dict) -> Country:
    items = json_db.load(COUNTRIES_FILE)
    clean = _clean(data)
    if any(i["city"].lower() == clean["city"].lower() for i in items):
        raise ServiceError(f"{clean['city']} already exists.")
    clean["id"] = json_db.next_id(items)
    country = Country.from_dict(clean)
    items.append(country.to_dict())
    json_db.save(COUNTRIES_FILE, items)
    return country


def update(country_id: int, changes: dict) -> Country:
    items = json_db.load(COUNTRIES_FILE)
    for i, raw in enumerate(items):
        if raw["id"] == country_id:
            clean = _clean({**raw, **changes})
            clean["id"] = country_id
            country = Country.from_dict(clean)
            items[i] = country.to_dict()
            json_db.save(COUNTRIES_FILE, items)
            return country
    raise ServiceError(f"No destination with ID {country_id}.")


def delete(country_id: int) -> None:
    items = json_db.load(COUNTRIES_FILE)
    remaining = [i for i in items if i["id"] != country_id]
    if len(remaining) == len(items):
        raise ServiceError(f"No destination with ID {country_id}.")
    json_db.save(COUNTRIES_FILE, remaining)
