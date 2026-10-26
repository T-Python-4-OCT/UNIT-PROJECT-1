from datetime import datetime

import storage
from models import Table


def add_table(capacity, location):
    try:
        capacity = int(capacity)
    except ValueError:
        raise ValueError("Seats must be a whole number.")
    if not 1 <= capacity <= 20:
        raise ValueError("Seats must be between 1 and 20.")
    tables = storage.load_tables()
    table = Table(max((t.id for t in tables), default=0) + 1, capacity, location.lower())
    tables.append(table)
    storage.save_tables(tables)
    return table


def remove_table(table_id):
    tables = storage.load_tables()
    if not any(t.id == table_id for t in tables):
        raise ValueError(f"No table with id {table_id}.")
    now = datetime.now()
    for r in storage.load_reservations():
        if r.table_id == table_id and r.status == "confirmed" and r.end_dt > now:
            raise ValueError(
                f"Table {table_id} has upcoming bookings (e.g. #{r.id} at {r.start}). "
                "Cancel them first."
            )
    storage.save_tables([t for t in tables if t.id != table_id])


def get_table(table_id):
    return next((t for t in storage.load_tables() if t.id == table_id), None)


def search_tables(keyword):
    
    keyword = keyword.lower()
    all_tables = storage.load_tables()
    if keyword.isdigit():
        found = [t for t in all_tables if t.capacity >= int(keyword)]
    else:
        found = [t for t in all_tables if keyword in t.location]
    return sorted(found, key=lambda t: t.capacity)
