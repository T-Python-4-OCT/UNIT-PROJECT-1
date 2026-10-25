from src.services.auth_service import register_user, login_user, load_users, migrate_passwords
from src.services.logistics_service import (
    view_supplies, add_supply_item, create_shipment, load_shipments,
    get_pending_shipments, assign_vehicle_to_shipment, create_field_request,
    load_field_requests,
)
from src.services.weather_api import get_crisis_weather
from src.services.recommend_service import get_smart_recommendations
from src.utils import display as ui

console = ui.console

REGIONS = {
    "1": {"name": "Riyadh", "lat": 24.7136, "lon": 46.6753},
    "2": {"name": "Tabuk", "lat": 28.3972, "lon": 36.5788},
    "3": {"name": "Jeddah", "lat": 21.5433, "lon": 39.1728},
    "4": {"name": "Dammam", "lat": 26.4207, "lon": 50.0888},
}

VEHICLES = [
    ("1", "Truck Alpha", "Ground", 500, True),
    ("2", "Cargo Drone Beta", "Air", 50, True),
    ("3", "Heavy Transporter Gamma", "Ground", 2000, False),
]


def show_supplies():
    ui.clear()
    ui.display_supplies_table(view_supplies())
    ui.pause()


def invalid():
    ui.error("Invalid option. Please try again.")


def manager_menu(user):
    while True:
        ui.clear()
        choice = ui.menu(f"Manager Dashboard ({user.user_name})", [
            "View Supplies Inventory", "Add New Supply Item",
            "View Active Shipments & Tracking", "View System Users", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            add_supply_item()
            ui.pause()
        elif choice == "3":
            ui.clear()
            shipments = load_shipments()
            if shipments:
                ui.display_shipments_table(shipments)
            else:
                console.print("[yellow]No shipments recorded yet.[/yellow]")
            ui.pause()
        elif choice == "4":
            ui.clear()
            users = load_users()
            if users:
                ui.display_users_table(users)
            else:
                console.print("[yellow]No registered users found.[/yellow]")
            ui.pause()
        elif choice == "5":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            invalid()
            ui.pause()


def pick_region():
    ui.clear()
    ui.title("Select Crisis Region")
    for k, r in REGIONS.items():
        console.print(f"  {k}. {r['name']}")
    return REGIONS.get(ui.ask("Choose region (1-4):"))


def dispatcher_menu(user):
    while True:
        ui.clear()
        choice = ui.menu(f"Dispatcher Dashboard ({user.user_name})", [
            "View Supplies Inventory", "View Field Supervisor Requests & Status",
            "Check Crisis Weather (Live API)", "Get Smart Supply Recommendations",
            "Create & Dispatch Shipment Request", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            ui.clear()
            requests = load_field_requests()
            if not requests:
                console.print("[yellow]No pending requests from field supervisors.[/yellow]")
            else:
                ui.display_field_requests_table(requests)
                console.print(f"\n[{ui.YELLOW}]Tip: You can now go to option 5 to create and dispatch a shipment based on these requests![/]")
            ui.pause()
        elif choice == "3":
            region = pick_region()
            if not region:
                ui.error("Invalid choice.")
            else:
                weather = get_crisis_weather(region["lat"], region["lon"])
                if weather:
                    ui.weather_panel(region["name"], weather)
                else:
                    ui.error("Could not fetch weather.")
            ui.pause()
        elif choice == "4":
            ui.clear()
            ui.heading("💡", "Smart Recommendations")
            category = ui.ask("Enter crisis category (Medical, Food, Shelter):")
            recs = get_smart_recommendations(category)
            if recs:
                ui.display_recommendations(recs, category)
            else:
                console.print("[yellow]No recommendations found.[/yellow]")
            ui.pause()
        elif choice == "5":
            ui.clear()
            create_shipment()
            ui.pause()
        elif choice == "6":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            invalid()
            ui.pause()


def field_supervisor_menu(user):
    zone = getattr(user, "crisis_zone", "General Zone")
    while True:
        ui.clear()
        choice = ui.menu(f"Field Supervisor Dashboard ({user.user_name} | Zone: {zone})", [
            "View Supplies Inventory", "Report Urgent Field Request (Send to Dispatcher)",
            "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            ui.clear()
            create_field_request(zone)
            ui.pause()
        elif choice == "3":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            invalid()
            ui.pause()


def fleet_status(specialty):
    from rich.table import Table
    ui.clear()
    t = Table(title=f"🚚 [bold {ui.VIOLET}]Fleet Status ({specialty} Unit)[/]", title_justify="left",
              border_style=ui.DIM, header_style=f"bold {ui.CYAN}")
    for c, kw in [("Vehicle", {}), ("Type", {}), ("Capacity (kg)", {"justify": "right"}), ("Status", {})]:
        t.add_column(c, **kw)
    for _, name, kind, cap, ready in VEHICLES:
        t.add_row(("🚁 " if kind == "Air" else "🚚 ") + name, kind, str(cap),
                  f"[{ui.GREEN}]Ready[/]" if ready else f"[{ui.YELLOW}]In Maintenance[/]")
    console.print(t)
    ui.pause()


def assign_flow():
    ui.clear()
    pending = get_pending_shipments()
    if not pending:
        console.print("[yellow]No pending shipments waiting for fleet assignment.[/yellow]")
        return
    ui.title("Pending Shipments Awaiting Fleet")
    for s in pending:
        console.print(f"📦 ID: [cyan]{s.get('shipment_id')}[/cyan] | Item: {s.get('quantity')}x {s.get('item_name')} | Destination: [magenta]{s.get('destination')}[/magenta]")

    target_id = ui.ask("Enter Shipment ID to process (e.g., SHP-101):")
    ship = next((s for s in pending if s.get("shipment_id", "").lower() == target_id.lower()), None)
    if not ship:
        ui.error("Shipment ID not found.")
        return

    dest = (ship.get("destination") or "").strip().lower()
    region = next((r for r in REGIONS.values() if r["name"].lower() == dest), REGIONS["1"])
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

    console.print("\nSelect Transport Vehicle:")
    for k, name, kind, cap, ready in VEHICLES:
        note = "" if ready else f"  [{ui.YELLOW}](In Maintenance)[/]"
        console.print(f"{k}. {name} ({kind} - {cap} kg){note}")
    v_choice = ui.ask("Choose vehicle (1-3):")
    chosen = next((v for v in VEHICLES if v[0] == v_choice), None)
    if not chosen or not chosen[4]:
        ui.error("That vehicle isn't available.")
        return

    sid = ship.get("shipment_id")
    if assign_vehicle_to_shipment(sid, chosen[1]):
        ui.ok(f"Shipment {sid} assigned to '{chosen[1]}' and marked 'In Transit'!")
        ui.simulate_dispatch_progress(sid, chosen[1], ship.get("destination"))
    else:
        ui.error("Assignment failed.")


def fleet_officer_menu(user):
    specialty = getattr(user, "specialty", "Logistics")
    while True:
        ui.clear()
        choice = ui.menu(f"Fleet Officer Dashboard ({user.user_name} | Specialty: {specialty})", [
            "View Supplies Inventory", "Check Fleet Vehicle Capacities",
            "Review Pending Shipments, Check Weather & Assign Vehicle", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            fleet_status(specialty)
        elif choice == "3":
            assign_flow()
            ui.pause()
        elif choice == "4":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            invalid()
            ui.pause()


def general_user_menu(user):
    while True:
        ui.clear()
        choice = ui.menu(f"General Dashboard ({user.user_name})", ["View Supplies Inventory", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            break
        else:
            invalid()
            ui.pause()


def main():
    migrate_passwords()
    while True:
        ui.clear()
        ui.display_header()
        choice = ui.menu("Main Menu", ["Login", "Register New User", "Exit Program"])
        if choice == "1":
            current_user = login_user()
            if current_user:
                role = current_user.get("role") if isinstance(current_user, dict) else getattr(current_user, "role", None)
                {"manager": manager_menu, "dispatcher": dispatcher_menu,
                 "field_supervisor": field_supervisor_menu,
                 "fleet_officer": fleet_officer_menu}.get(role, general_user_menu)(current_user)
            else:
                ui.pause()
        elif choice == "2":
            register_user()
            ui.pause()
        elif choice == "3":
            console.print("\n[bold green]Exiting program. Stay safe![/bold green]")
            break
        else:
            invalid()
            ui.pause()


if __name__ == "__main__":
    main()