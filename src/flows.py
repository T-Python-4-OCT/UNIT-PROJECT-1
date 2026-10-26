
from src import config
from src.services import logistics_service as logistics
from src.services.weather_api import get_crisis_weather
from src.utils import display as ui

console = ui.console


def ask_int(label, default=None, minimum=1, maximum=None):
    """Ask until a valid whole number is typed. Empty = default (or cancel -> None)."""
    hint = f"[{default}]" if default is not None else "(leave empty to cancel)"
    while True:
        raw = ui.ask(f"{label} {hint}:")
        if not raw:
            return default
        if raw.isdigit() and int(raw) >= minimum and (maximum is None or int(raw) <= maximum):
            return int(raw)
        limit = f" between {minimum} and {maximum}" if maximum is not None else f" of at least {minimum}"
        ui.error(f"Enter a whole number{limit}.")


def ask_float(label, minimum_exclusive=0.0):
    while True:
        raw = ui.ask(f"{label} (leave empty to cancel):")
        if not raw:
            return None
        try:
            value = float(raw)
            if value > minimum_exclusive:
                return value
        except ValueError:
            pass
        ui.error(f"Enter a number greater than {minimum_exclusive:g}.")


def ask_region(title="Select Destination Zone"):
    names = [r["name"] for r in config.REGIONS] + ["Other (type it)"]
    idx = ui.select(title, names, prompt="Choose zone")
    if idx < 0:
        return None
    if idx == len(names) - 1:
        return ui.ask("Enter destination zone:") or None
    return names[idx]


def region_by_name(name):
    return next((r for r in config.REGIONS if r["name"].lower() == (name or "").strip().lower()),
                config.REGIONS[0])


# ------------------------------------------------------------------ manager
def add_supply_flow():
    ui.clear()
    ui.heading("📦", "Add New Supply Item", color=None)
    name = ui.ask("Enter item name (leave empty to cancel):")
    if not name:
        return
    known = sorted({s.get("category", "") for s in logistics.load_supplies() if s.get("category")})
    idx = ui.select("Category", known + ["New category…"], prompt="Choose category")
    category = ui.ask("Enter the new category:") if idx == len(known) or idx < 0 else known[idx]
    quantity = ask_int("Enter quantity", minimum=0)
    if quantity is None:
        return
    weight = ask_float("Enter unit weight (kg)")
    if weight is None:
        return
    ok, msg, _ = logistics.add_supply(name, category, quantity, weight)
    (ui.ok if ok else ui.error)(msg)


# --------------------------------------------------------- field supervisor
def field_request_flow(zone):
    ui.clear()
    ui.heading("🚨", "Report Urgent Field Request", color=None)
    item = ui.ask("Enter required material name (leave empty to cancel):")
    if not item:
        return
    quantity = ask_int("Enter required quantity")
    if quantity is None:
        return
    idx = ui.select("Priority", config.PRIORITIES, prompt="Choose priority")
    priority = config.PRIORITIES[idx] if idx >= 0 else "Medium"
    ok, msg, _ = logistics.create_field_request(zone, item, quantity, priority)
    (ui.ok if ok else ui.error)(msg)


# --------------------------------------------------------------- dispatcher
def create_shipment_flow():
    ui.clear()
    supplies = [s for s in logistics.load_supplies() if s.get("quantity", 0) > 0]
    if not supplies:
        ui.error("No supplies available in inventory to ship.")
        return
    ui.display_supplies_table(supplies)

    labels = [f"{s['id']} · {s['name']} (available: {s['quantity']})" for s in supplies]
    idx = ui.select("Select supply to dispatch", labels, prompt="Choose item")
    if idx < 0:
        return
    item = supplies[idx]

    request = None
    pending = logistics.open_requests()
    if pending:
        options = ["No linked request"] + [
            f"{r['request_id']} · {r['quantity']}x {r['item_name']} · {r['zone']} [{r.get('priority', 'Medium')}]"
            for r in pending]
        r_idx = ui.select("Which field request is this for?", options, prompt="Choose request")
        request = pending[r_idx - 1] if r_idx > 0 else None

    default_qty = min(request["quantity"], item["quantity"]) if request else None
    quantity = ask_int(f"Quantity to ship (max {item['quantity']})", default=default_qty,
                       maximum=item["quantity"])
    if quantity is None:
        return

    destination = ask_region()
    if not destination:
        return
    ok, msg, ship = logistics.create_shipment(item["id"], quantity, destination,
                                              request["request_id"] if request else None)
    if ok:
        ui.ok(msg)
        ui.info(f"Estimated weight: {ship['total_weight_kg']:g} kg")
    else:
        ui.error(msg)


# ------------------------------------------------------------ fleet officer
def pick_shipment(shipments, title):
    labels = [f"{s['shipment_id']} · {s['quantity']}x {s['item_name']} → {s['destination']}"
              + (f" ({s['total_weight_kg']:g} kg)" if s.get("total_weight_kg") else "")
              for s in shipments]
    idx = ui.select(title, labels, prompt="Choose shipment")
    return shipments[idx] if idx >= 0 else None


def assign_flow():
    ui.clear()
    pending = logistics.pending_shipments()
    if not pending:
        console.print("[yellow]No pending shipments waiting for fleet assignment.[/yellow]")
        return
    ship = pick_shipment(pending, "Pending Shipments Awaiting Fleet")
    if not ship:
        return

    region = region_by_name(ship.get("destination"))
    ui.info(f"Checking live weather for destination '{ship.get('destination')}'...")
    weather = get_crisis_weather(region["lat"], region["lon"])
    if weather:
        ui.weather_panel(region["name"], weather)
        if (weather.get("windspeed") or 0) > 30:
            console.print(f"[bold {ui.RED}]⚠️  High winds detected! Air drones not recommended. Use ground trucks.[/]")
        else:
            console.print(f"[bold {ui.GREEN}]✨ Weather is stable for all transport options.[/]")
    else:
        console.print("[yellow]Could not fetch live weather data.[/yellow]")

    labels = []
    for v in config.VEHICLES:
        problem = logistics.vehicle_problem(v, ship)
        labels.append(f"{v['name']} ({v['kind']} - {v['capacity_kg']} kg)" + (f"  [{problem}]" if problem else ""))
    v_idx = ui.select("Select Transport Vehicle", labels, prompt="Choose vehicle")
    if v_idx < 0:
        return

    sid = ship["shipment_id"]
    ok, msg = logistics.assign_vehicle(sid, config.VEHICLES[v_idx]["name"])
    if ok:
        ui.ok(msg)
        ui.simulate_dispatch_progress(sid, config.VEHICLES[v_idx]["name"], ship.get("destination"))
    else:
        ui.error(msg)


def deliver_flow():
    ui.clear()
    moving = logistics.in_transit_shipments()
    if not moving:
        console.print("[yellow]No shipments are currently in transit.[/yellow]")
        return
    ship = pick_shipment(moving, "Shipments In Transit")
    if not ship:
        return
    ok, msg = logistics.mark_delivered(ship["shipment_id"])
    (ui.ok if ok else ui.error)(msg)