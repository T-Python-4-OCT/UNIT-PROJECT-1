
import re

from src import config
from src.models.field_request import FieldRequest
from src.models.shipment import Shipment
from src.models.supply import SupplyItem
from src.utils.json_handler import load_json, save_json


def load_supplies():
    return load_json(config.data_path(config.SUPPLIES_FILE))


def save_supplies(supplies):
    save_json(config.data_path(config.SUPPLIES_FILE), supplies)


def load_shipments():
    return load_json(config.data_path(config.SHIPMENTS_FILE))


def save_shipments(shipments):
    save_json(config.data_path(config.SHIPMENTS_FILE), shipments)


def load_field_requests():
    return load_json(config.data_path(config.REQUESTS_FILE))


def save_field_requests(requests):
    save_json(config.data_path(config.REQUESTS_FILE), requests)


def view_supplies():
    return load_supplies()


def next_id(existing_ids, prefix, width=3, start=0):
    """'SUPP' + ['SUPP-009', 'SUPP-012'] -> 'SUPP-013' (highest number + 1, never reused)."""
    numbers = [int(m.group(1)) for i in existing_ids
               if (m := re.fullmatch(rf"{prefix}-(\d+)", str(i or "")))]
    return f"{prefix}-{max(numbers, default=start) + 1:0{width}d}"


def find_supply(supplies, item_id):
    return next((s for s in supplies if s.get("id") == item_id), None)


def get_vehicle(name):
    return next((v for v in config.VEHICLES if v["name"] == name), None)


def vehicle_problem(vehicle, shipment):
    """Why this vehicle can't take this shipment ('' when it can)."""
    if not vehicle["ready"]:
        return "in maintenance"
    weight = shipment.get("total_weight_kg")
    if weight and weight > vehicle["capacity_kg"]:
        return f"over capacity ({weight:g} kg > {vehicle['capacity_kg']} kg)"
    return ""


def add_supply(name, category, quantity, unit_weight_kg):
    name, category = " ".join(str(name).split()), " ".join(str(category).split()).title()
    if not name or not category:
        return False, "Name and category are required.", None
    try:
        quantity, unit_weight_kg = int(quantity), float(unit_weight_kg)
    except (TypeError, ValueError):
        return False, "Quantity must be a whole number and weight a number.", None
    if quantity < 0:
        return False, "Quantity can't be negative.", None
    if unit_weight_kg <= 0:
        return False, "Unit weight must be greater than zero.", None

    supplies = load_supplies()
    item = SupplyItem(next_id([s.get("id") for s in supplies], "SUPP"), name, category,
                      quantity, round(unit_weight_kg, 3)).to_dict()
    supplies.append(item)
    save_supplies(supplies)
    return True, f"Item '{name}' ({item['id']}) added to inventory.", item


def create_field_request(zone, item_name, quantity, priority="Medium"):
    item_name = " ".join(str(item_name).split())
    if not item_name:
        return False, "Material name is required.", None
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return False, "Quantity must be a whole number.", None
    if quantity <= 0:
        return False, "Quantity must be greater than zero.", None
    if priority not in config.PRIORITIES:
        priority = "Medium"

    requests = load_field_requests()
    req = FieldRequest(next_id([r.get("request_id") for r in requests], "REQ", start=100),
                       item_name, quantity, zone, priority).to_dict()
    requests.append(req)
    save_field_requests(requests)
    return True, f"Request {req['request_id']} for {quantity}x '{item_name}' sent to the dispatcher.", req


def open_requests():
    """Requests still waiting for a shipment, most urgent first."""
    order = {p: i for i, p in enumerate(config.PRIORITIES)}
    pending = [r for r in load_field_requests() if r.get("status") == config.REQ_PENDING]
    return sorted(pending, key=lambda r: order.get(r.get("priority", "Medium"), 1))


def _set_request_status(requests, request_id, status):
    for r in requests:
        if request_id and r.get("request_id") == request_id:
            r["status"] = status
            return True
    return False


def create_shipment(item_id, quantity, destination, request_id=None):
    """Take stock out of the inventory and queue a shipment for the fleet officer."""
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return False, "Quantity must be a whole number.", None
    destination = " ".join(str(destination).split()).title()
    if not destination:
        return False, "Destination is required.", None

    supplies = load_supplies()
    item = find_supply(supplies, item_id)
    if not item:
        return False, "Supply item not found.", None
    if quantity <= 0:
        return False, "Quantity must be greater than zero.", None
    if quantity > item["quantity"]:
        return False, f"Only {item['quantity']} in stock.", None

    requests = load_field_requests()
    if request_id:
        linked = next((r for r in requests if r.get("request_id") == request_id), None)
        if not linked or linked.get("status") != config.REQ_PENDING:
            return False, f"Request {request_id} isn't waiting for a shipment.", None

    shipments = load_shipments()
    shipment = Shipment(
        next_id([s.get("shipment_id") for s in shipments], "SHP", start=100),
        item["name"], quantity, destination,
        total_weight_kg=round(quantity * item["unit_weight_kg"], 3), request_id=request_id).to_dict()

    item["quantity"] -= quantity
    shipments.append(shipment)
    _set_request_status(requests, request_id, config.REQ_APPROVED)
    save_shipments(shipments)
    save_field_requests(requests)
    save_supplies(supplies)
    return True, f"Shipment {shipment['shipment_id']} created and sent to the fleet officer.", shipment


def pending_shipments():
    return [s for s in load_shipments() if s.get("status") == config.SHIP_PENDING]


def in_transit_shipments():
    return [s for s in load_shipments() if s.get("status") == config.SHIP_IN_TRANSIT]


def assign_vehicle(shipment_id, vehicle_name):
    vehicle = get_vehicle(vehicle_name)
    if not vehicle:
        return False, "Unknown vehicle."
    shipments = load_shipments()
    data = next((s for s in shipments if s.get("shipment_id") == shipment_id
                 and s.get("status") == config.SHIP_PENDING), None)
    if not data:
        return False, "Shipment not found or already assigned."
    problem = vehicle_problem(vehicle, data)
    if problem:
        return False, f"{vehicle['name']} can't take it: {problem}."

    shipment = Shipment.from_dict(data)
    shipment.assign(vehicle["name"])
    data.update(shipment.to_dict())
    requests = load_field_requests()
    if _set_request_status(requests, shipment.request_id, config.REQ_IN_TRANSIT):
        save_field_requests(requests)
    save_shipments(shipments)
    return True, f"Shipment {shipment_id} assigned to '{vehicle['name']}' and marked 'In Transit'."


def mark_delivered(shipment_id):
    shipments = load_shipments()
    data = next((s for s in shipments if s.get("shipment_id") == shipment_id
                 and s.get("status") == config.SHIP_IN_TRANSIT), None)
    if not data:
        return False, "Shipment not found or not in transit."
    shipment = Shipment.from_dict(data)
    shipment.deliver()
    data.update(shipment.to_dict())
    requests = load_field_requests()
    if _set_request_status(requests, shipment.request_id, config.REQ_DONE):
        save_field_requests(requests)
    save_shipments(shipments)
    return True, f"Shipment {shipment_id} delivered. Request closed."