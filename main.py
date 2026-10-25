from src.services.auth_service import register_user, login_user, load_users
from src.services.logistics_service import (
    view_supplies, add_supply_item, create_shipment, load_shipments, 
    get_pending_shipments, assign_vehicle_to_shipment, create_field_request, 
    load_field_requests, display_field_requests_table
)
from src.services.weather_api import get_crisis_weather
from src.services.recommend_service import get_smart_recommendations
from src.utils.display import display_header, display_supplies_table, simulate_dispatch_progress
from rich.console import Console

console = Console()

def manager_menu(user):
    while True:
        console.print(f"\n[bold cyan]--- Manager Dashboard ({user.user_name}) ---[/bold cyan]")
        console.print("1. View Supplies Inventory")
        console.print("2. Add New Supply Item")
        console.print("3. View Active Shipments & Tracking")
        console.print("4. View System Users")
        console.print("5. Logout / Switch User")
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
            
        elif choice == "2":
            add_supply_item()
            
        elif choice == "3":
            console.print("\n[bold yellow]--- Active Shipments & Tracking ---[/bold yellow]")
            shipments = load_shipments()
            if shipments:
                for s in shipments:
                    status_color = "green" if "Transit" in s.get('status', '') or "Completed" in s.get('status', '') else "yellow"
                    veh = s.get('vehicle') or "Unassigned"
                    console.print(f"📦 [{s.get('shipment_id')}]: {s.get('quantity')}x {s.get('item_name')} -> {s.get('destination')} | Vehicle: [magenta]{veh}[/magenta] | Status: [{status_color}]{s.get('status')}[/{status_color}]")
            else:
                console.print("[yellow]No shipments recorded yet.[/yellow]")
            
        elif choice == "4":
            console.print("\n[bold yellow]--- Registered System Users ---[/bold yellow]")
            users = load_users()
            if users:
                for idx, u in enumerate(users, 1):
                    role_str = u.get('role', 'general')
                    username = u.get('user_name', 'Unknown')
                    email = u.get('email', 'N/A')
                    console.print(f"{idx}. User: [cyan]{username}[/cyan] | Role: [green]{role_str}[/green] | Email: {email}")
            else:
                console.print("[yellow]No registered users found in database yet.[/yellow]")
                
        elif choice == "5":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


def dispatcher_menu(user):
    while True:
        console.print(f"\n[bold cyan]--- Dispatcher Dashboard ({user.user_name}) ---[/bold cyan]")
        console.print("1. View Supplies Inventory")
        console.print("2. View Field Supervisor Requests & Status")
        console.print("3. Check Crisis Weather (Live API)")
        console.print("4. Get Smart Supply Recommendations")
        console.print("5. Create & Dispatch Shipment Request")
        console.print("6. Logout / Switch User")
        
        choice = input("Choose an option (1-6): ").strip()
        
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
            
        elif choice == "2":
            requests = load_field_requests()
            if not requests:
                console.print("[yellow]No pending requests from field supervisors.[/yellow]")
            else:
                display_field_requests_table(requests)
                console.print("\n[cyan]Tip: You can now go to option 5 to create and dispatch this shipment based on these requests![/cyan]")
                
        elif choice == "3":
            console.print("\n[bold yellow]--- Select Crisis Region ---[/bold yellow]")
            console.print("1. Riyadh\n2. Tabuk\n3. Jeddah\n4. Dammam")
            reg_choice = input("Choose region (1-4): ").strip()
            regions_map = {
                "1": {"name": "Riyadh", "lat": 24.7136, "lon": 46.6753},
                "2": {"name": "Tabuk", "lat": 28.3972, "lon": 36.5788},
                "3": {"name": "Jeddah", "lat": 21.5433, "lon": 39.1728},
                "4": {"name": "Dammam", "lat": 26.4207, "lon": 50.0888}
            }
            if reg_choice in regions_map:
                r = regions_map[reg_choice]
                weather = get_crisis_weather(r["lat"], r["lon"])
                if weather:
                    console.print(f"\n[bold green]Weather in {r['name']}:[/bold green] Temp: {weather.get('temperature')}°C | Wind: {weather.get('windspeed')} km/h")
                else:
                    console.print("[bold red]Could not fetch weather.[/bold red]")
            else:
                console.print("[bold red]Invalid choice.[/bold red]")
                
        elif choice == "4":
            category = input("Enter crisis category (Medical, Food, Shelter): ").strip()
            recs = get_smart_recommendations(category)
            if recs:
                console.print(f"\n[bold magenta]Smart Recommendations:[/bold magenta]")
                display_supplies_table(recs)
            else:
                console.print("[yellow]No recommendations found.[/yellow]")
                
        elif choice == "5":
            create_shipment()
                
        elif choice == "6":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


def field_supervisor_menu(user):
    while True:
        zone = getattr(user, "crisis_zone", "General Zone")
        console.print(f"\n[bold cyan]--- Field Supervisor Dashboard ({user.user_name} | Zone: {zone}) ---[/bold cyan]")
        console.print("1. View Supplies Inventory")
        console.print("2. Report Urgent Field Request (Send to Dispatcher)")
        console.print("3. Logout / Switch User")
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
        elif choice == "2":
            create_field_request(zone)
        elif choice == "3":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


def fleet_officer_menu(user):
    while True:
        specialty = getattr(user, "specialty", "Logistics")
        console.print(f"\n[bold cyan]--- Fleet Officer Dashboard ({user.user_name} | Specialty: {specialty}) ---[/bold cyan]")
        console.print("1. View Supplies Inventory")
        console.print("2. Check Fleet Vehicle Capacities")
        console.print("3. Review Pending Shipments, Check Weather & Assign Vehicle")
        console.print("4. Logout / Switch User")
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
        elif choice == "2":
            console.print(f"\n[bold yellow]--- Fleet Status ({specialty} Unit) ---[/bold yellow]")
            console.print("🚚 Truck Alpha (Ground - Capacity: 500 kg) - [green]Ready[/green]")
            console.print("🚁 Cargo Drone Beta (Air - Capacity: 50 kg) - [green]Ready[/green]")
            console.print("🚛 Heavy Transporter Gamma (Ground - Capacity: 2000 kg) - [yellow]In Maintenance[/yellow]")
        elif choice == "3":
            pending = get_pending_shipments()
            if not pending:
                console.print("[yellow]No pending shipments waiting for fleet assignment.[/yellow]")
            else:
                console.print("\n[bold yellow]--- Pending Shipments Awaiting Fleet ---[/bold yellow]")
                for s in pending:
                    console.print(f"📦 ID: [cyan]{s.get('shipment_id')}[/cyan] | Item: {s.get('quantity')}x {s.get('item_name')} | Destination: [magenta]{s.get('destination')}[/magenta]")
                
                target_id = input("Enter Shipment ID to process (e.g., SHP-101): ").strip()
                selected_shipment = next((s for s in pending if s.get('shipment_id').lower() == target_id.lower()), None)
                
                if not selected_shipment:
                    console.print("[bold red]❌ Shipment ID not found.[/bold red]")
                else:
                    dest = selected_shipment.get('destination').strip().lower()
                    regions_coords = {
                        "riyadh": {"lat": 24.7136, "lon": 46.6753},
                        "tabuk": {"lat": 28.3972, "lon": 36.5788},
                        "jeddah": {"lat": 21.5433, "lon": 39.1728},
                        "dammam": {"lat": 26.4207, "lon": 50.0888}
                    }
                    
                    coords = regions_coords.get(dest, {"lat": 24.7136, "lon": 46.6753})
                    console.print(f"[cyan]Checking live weather for destination '{selected_shipment.get('destination')}'...[/cyan]")
                    weather = get_crisis_weather(coords["lat"], coords["lon"])
                    
                    if weather:
                        temp = weather.get('temperature')
                        wind = weather.get('windspeed', 0)
                        console.print(f"🌡️ Temperature: {temp}°C | 💨 Wind Speed: {wind} km/h")
                        if wind > 30:
                            console.print("[bold red]⚠️ High winds detected! Air drones not recommended. Use ground trucks.[/bold red]")
                        else:
                            console.print("[bold green]✨ Weather is stable for all transport options.[/bold green]")
                    else:
                        console.print("[yellow]Could not fetch live weather data.[/yellow]")
                        
                    console.print("\nSelect Transport Vehicle:")
                    console.print("1. Truck Alpha (Ground - 500 kg)")
                    console.print("2. Cargo Drone Beta (Air - 50 kg)")
                    console.print("3. Heavy Transporter Gamma (Ground - 2000 kg)")
                    
                    v_choice = input("Choose vehicle (1-3): ").strip()
                    v_map = {"1": "Truck Alpha", "2": "Cargo Drone Beta", "3": "Heavy Transporter Gamma"}
                    chosen_vehicle = v_map.get(v_choice, "Truck Alpha")
                    
                    if assign_vehicle_to_shipment(selected_shipment.get('shipment_id'), chosen_vehicle):
                        console.print(f"[bold green]✅ Shipment {selected_shipment.get('shipment_id')} assigned to '{chosen_vehicle}' and marked 'In Transit'![/bold green]")
                        simulate_dispatch_progress(selected_shipment.get('shipment_id'))
                    else:
                        console.print("[bold red]❌ Assignment failed.[/bold red]")
        elif choice == "4":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


def general_user_menu(user):
    while True:
        console.print(f"\n[bold cyan]--- General Dashboard ({user.user_name}) ---[/bold cyan]")
        console.print("1. View Supplies Inventory")
        console.print("2. Logout / Switch User")
        choice = input("Choose an option (1-2): ").strip()
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
        elif choice == "2":
            break
        else:
            console.print("[bold red]Invalid option.[/bold red]")


def main():
    display_header()
    while True:
        console.print("\n[bold yellow]--- Main Menu ---[/bold yellow]")
        console.print("1. Login")
        console.print("2. Register New User")
        console.print("3. Exit Program")
        
        main_choice = input("Choose an option (1-3): ").strip()
        
        if main_choice == "1":
            current_user = login_user()
            if current_user:
                role = current_user.get("role") if isinstance(current_user, dict) else getattr(current_user, "role", None)
                if role == "manager":
                    manager_menu(current_user)
                elif role == "dispatcher":
                    dispatcher_menu(current_user)
                elif role == "field_supervisor":
                    field_supervisor_menu(current_user)
                elif role == "fleet_officer":
                    fleet_officer_menu(current_user)
                else:
                    general_user_menu(current_user)
        elif main_choice == "2":
            register_user()
        elif main_choice == "3":
            console.print("\n[bold green]Exiting program. Stay safe![/bold green]")
            break
        else:
            console.print("[bold red]Invalid choice.[/bold red]")

if __name__ == "__main__":
    main()