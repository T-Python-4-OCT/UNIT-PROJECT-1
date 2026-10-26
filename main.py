from rich.table import Table

from src import config, flows
from src.services import logistics_service as logistics
from src.services.auth_service import login_user, register_user, load_users
from src.services.migrations import run_migrations
from src.services.recommend_service import get_smart_recommendations
from src.services.weather_api import get_crisis_weather
from src.utils import display as ui

console = ui.console


def show_supplies():
    ui.clear()
    ui.display_supplies_table(logistics.view_supplies())
    ui.pause()


def show_table(rows, draw, empty_message):
    ui.clear()
    if rows:
        draw(rows)
    else:
        console.print(f"[yellow]{empty_message}[/yellow]")
    ui.pause()


def logout():
    console.print("[yellow]Logging out...[/yellow]")


def manager_menu(user):
    while True:
        ui.clear()
        choice = ui.menu(f"Manager Dashboard ({user.user_name})", [
            "View Supplies Inventory", "Add New Supply Item",
            "View Active Shipments & Tracking", "View System Users",
            "Create Manager / Staff Account", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            flows.add_supply_flow()
            ui.pause()
        elif choice == "3":
            show_table(logistics.load_shipments(), ui.display_shipments_table, "No shipments recorded yet.")
        elif choice == "4":
            show_table(load_users(), ui.display_users_table, "No registered users found.")
        elif choice == "5":
            ui.clear()
            register_user(allowed_roles=config.ROLES)
            ui.pause()
        elif choice == "6":
            logout()
            break


def pick_region():
    ui.clear()
    names = [r["name"] for r in config.REGIONS]
    idx = ui.select("Select Crisis Region", names, prompt="Choose region")
    return config.REGIONS[idx] if idx >= 0 else None


def recommendations_screen():
    ui.clear()
    ui.heading("💡", "Smart Recommendations")
    categories = sorted({s.get("category", "") for s in logistics.load_supplies() if s.get("category")})
    if not categories:
        console.print("[yellow]No supplies recorded yet.[/yellow]")
        return
    idx = ui.select("Crisis category", categories, prompt="Choose category")
    if idx < 0:
        return
    recs = get_smart_recommendations(categories[idx])
    if recs:
        ui.display_recommendations(recs, categories[idx])
    else:
        console.print("[yellow]No recommendations found.[/yellow]")


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
            requests = logistics.load_field_requests()
            if not requests:
                console.print("[yellow]No requests from field supervisors yet.[/yellow]")
            else:
                ui.display_field_requests_table(requests)
                console.print(f"\n[{ui.YELLOW}]Tip: use option 5 to create a shipment for a pending request.[/]")
            ui.pause()
        elif choice == "3":
            region = pick_region()
            if region:
                weather = get_crisis_weather(region["lat"], region["lon"])
                if weather:
                    ui.weather_panel(region["name"], weather)
                else:
                    ui.error("Could not fetch weather.")
                ui.pause()
        elif choice == "4":
            recommendations_screen()
            ui.pause()
        elif choice == "5":
            flows.create_shipment_flow()
            ui.pause()
        elif choice == "6":
            logout()
            break


def field_supervisor_menu(user):
    zone = getattr(user, "crisis_zone", "General Zone")
    while True:
        ui.clear()
        choice = ui.menu(f"Field Supervisor Dashboard ({user.user_name} | Zone: {zone})", [
            "View Supplies Inventory", "Report Urgent Field Request (Send to Dispatcher)",
            "Track My Requests", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            flows.field_request_flow(zone)
            ui.pause()
        elif choice == "3":
            mine = [r for r in logistics.load_field_requests()
                    if (r.get("zone") or "").lower() == zone.lower()]
            show_table(mine, ui.display_field_requests_table, "You haven't sent any requests yet.")
        elif choice == "4":
            logout()
            break


def fleet_status(specialty):
    ui.clear()
    table = Table(title=f"🚚 [bold {ui.VIOLET}]Fleet Status ({specialty} Unit)[/]", title_justify="left",
                  border_style=ui.DIM, header_style=f"bold {ui.CYAN}")
    for col, kw in [("Vehicle", {}), ("Type", {}), ("Capacity (kg)", {"justify": "right"}), ("Status", {})]:
        table.add_column(col, **kw)
    for v in config.VEHICLES:
        table.add_row(("🚁 " if v["kind"] == "Air" else "🚚 ") + v["name"], v["kind"], str(v["capacity_kg"]),
                      f"[{ui.GREEN}]Ready[/]" if v["ready"] else f"[{ui.YELLOW}]In Maintenance[/]")
    console.print(table)
    ui.pause()


def fleet_officer_menu(user):
    specialty = getattr(user, "specialty", "Logistics")
    while True:
        ui.clear()
        choice = ui.menu(f"Fleet Officer Dashboard ({user.user_name} | Specialty: {specialty})", [
            "View Supplies Inventory", "Check Fleet Vehicle Capacities",
            "Review Pending Shipments, Check Weather & Assign Vehicle",
            "Mark Shipment as Delivered", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            fleet_status(specialty)
        elif choice == "3":
            flows.assign_flow()
            ui.pause()
        elif choice == "4":
            flows.deliver_flow()
            ui.pause()
        elif choice == "5":
            logout()
            break


def general_user_menu(user):
    while True:
        ui.clear()
        choice = ui.menu(f"General Dashboard ({user.user_name})", ["View Supplies Inventory", "Logout / Switch User"])
        if choice == "1":
            show_supplies()
        elif choice == "2":
            break


MENUS = {"manager": manager_menu, "dispatcher": dispatcher_menu,
         "field_supervisor": field_supervisor_menu, "fleet_officer": fleet_officer_menu}


def main():
    run_migrations()
    while True:
        ui.clear()
        ui.display_header()
        choice = ui.menu("Main Menu", ["Login", "Register New User", "Exit Program"])
        if choice == "1":
            user = login_user()
            if user:
                MENUS.get(user.role, general_user_menu)(user)
            else:
                ui.pause()
        elif choice == "2":
            ui.clear()
            register_user()
            ui.pause()
        elif choice == "3":
            console.print("\n[bold green]Exiting program. Stay safe![/bold green]")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold green]Session ended. Stay safe![/bold green]")