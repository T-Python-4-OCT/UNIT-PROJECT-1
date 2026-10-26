
from src import config
from src.utils.json_handler import load_json, save_json

OLD_SHIPMENT_STATUS = {
    "Pending": config.SHIP_PENDING,
    "Completed & In Transit": config.SHIP_IN_TRANSIT,   
}
OLD_REQUEST_STATUS = {
    "In Transit / Processed": config.REQ_APPROVED,
    "Completed (Dispatched)": config.REQ_DONE,
}


def _first(d, keys, default=None):
    return next((d[k] for k in keys if k in d and d[k] not in (None, "")), default)


def _num(value, cast, default):
    try:
        return cast(value)
    except (TypeError, ValueError):
        return default


def _migrate_supplies(path):
    """One shape: id, name, category, quantity, unit_weight_kg (older files had duplicate keys)."""
    supplies = load_json(path)
    out, used = [], []
    for item in supplies:
        old_id = str(_first(item, ["id", "item_id", "SUPP_ID", "code"], "")).strip()
        out.append({"_old": item, "_id": old_id if old_id.startswith("SUPP-") else None})
        if old_id.startswith("SUPP-"):
            used.append(old_id)
    top = max([int(i.split("-")[1]) for i in used if i.split("-")[1].isdigit()], default=0)
    result = []
    for entry in out:
        item, item_id = entry["_old"], entry["_id"]
        if item_id is None:
            top += 1
            item_id = f"SUPP-{top:03d}"
        result.append({
            "id": item_id,
            "name": str(_first(item, ["name", "item_name", "title"], "Unknown Item")).strip(),
            "category": str(_first(item, ["category", "type"], "General")).strip(),
            "quantity": _num(_first(item, ["quantity", "qty", "stock"], 0), int, 0),
            "unit_weight_kg": _num(_first(item, ["unit_weight_kg", "unit_weight", "weight", "kg"], 0), float, 0.0),
        })
    if result != supplies:
        save_json(path, result)
        return True
    return False


def _migrate_shipments(path, supplies):
    """Old records came in two shapes; both become the flat Shipment shape."""
    weights = {s["name"]: s["unit_weight_kg"] for s in supplies}
    shipments = load_json(path)
    result = []
    for s in shipments:
        if "items" in s:                                    
            items = s.get("items") or []
            item_name = items[0]["item_name"] if items else "—"
            quantity = sum(i.get("quantity", 0) for i in items)
            destination = s.get("destination_crisis", "")
            total = s.get("total_weight_kg")
        else:
            item_name, quantity = s.get("item_name", "—"), s.get("quantity", 0)
            destination, total = s.get("destination", ""), s.get("total_weight_kg")
        if total is None and item_name in weights:
            total = round(quantity * weights[item_name], 3)
        status = s.get("status", config.SHIP_PENDING)
        result.append({
            "shipment_id": s.get("shipment_id"),
            "item_name": item_name,
            "quantity": quantity,
            "destination": " ".join(str(destination).split()).title(),
            "total_weight_kg": total,
            "request_id": s.get("request_id"),
            "status": OLD_SHIPMENT_STATUS.get(status, status),
            "vehicle": s.get("vehicle"),
        })
    if result != shipments:
        save_json(path, result)
        return True
    return False


def _migrate_requests(path):
    requests = load_json(path)
    changed = False
    for r in requests:
        before = dict(r)
        r["status"] = OLD_REQUEST_STATUS.get(r.get("status"), r.get("status", config.REQ_PENDING))
        r.setdefault("priority", "Medium")
        if r != before:
            changed = True
    if changed:
        save_json(path, requests)
    return changed


def run_migrations():
    """Returns the names of the files that were upgraded (empty list = nothing to do)."""
    from src.services.auth_service import migrate_passwords

    changed = []
    supplies_path = config.data_path(config.SUPPLIES_FILE)
    if _migrate_supplies(supplies_path):
        changed.append("supplies")
    if _migrate_shipments(config.data_path(config.SHIPMENTS_FILE), load_json(supplies_path)):
        changed.append("shipments")
    if _migrate_requests(config.data_path(config.REQUESTS_FILE)):
        changed.append("field requests")
    if migrate_passwords():
        changed.append("passwords")
    return changed