"""Project-wide constants (paths, regions, fleet, roles, statuses) in one place."""
import os

DATA_DIR = "data"


def data_path(filename: str) -> str:
    """Resolved at call time so tests can point DATA_DIR at a temporary folder."""
    return os.path.join(DATA_DIR, filename)


USERS_FILE = "users.json"
SUPPLIES_FILE = "supplies.json"
SHIPMENTS_FILE = "shipments.json"
REQUESTS_FILE = "field_requests.json"

REGIONS = [
    {"name": "Riyadh", "lat": 24.7136, "lon": 46.6753},
    {"name": "Tabuk", "lat": 28.3972, "lon": 36.5788},
    {"name": "Jeddah", "lat": 21.5433, "lon": 39.1728},
    {"name": "Dammam", "lat": 26.4207, "lon": 50.0888},
]

VEHICLES = [
    {"name": "Truck Alpha", "kind": "Ground", "capacity_kg": 500, "ready": True},
    {"name": "Cargo Drone Beta", "kind": "Air", "capacity_kg": 50, "ready": True},
    {"name": "Heavy Transporter Gamma", "kind": "Ground", "capacity_kg": 2000, "ready": False},
]

PRIORITIES = ["High", "Medium", "Low"]

# (label, key). Everyone can self-register as the PUBLIC_ROLES; Manager and
# Dispatcher accounts can only be created by a logged-in manager.
ROLES = [
    ("Manager", "manager"),
    ("Dispatcher", "dispatcher"),
    ("Field Supervisor", "field_supervisor"),
    ("Fleet Officer", "fleet_officer"),
    ("General User", "general"),
]
PUBLIC_ROLES = [r for r in ROLES if r[1] in ("field_supervisor", "fleet_officer", "general")]

# Shipment lifecycle:  Pending Fleet Assignment -> In Transit -> Completed
SHIP_PENDING = "Pending Fleet Assignment"
SHIP_IN_TRANSIT = "In Transit"
SHIP_DONE = "Completed"

# Field-request lifecycle:  Pending -> Approved (shipment created) -> In Transit -> Completed
REQ_PENDING = "Pending"
REQ_APPROVED = "Approved"
REQ_IN_TRANSIT = "In Transit"
REQ_DONE = "Completed"