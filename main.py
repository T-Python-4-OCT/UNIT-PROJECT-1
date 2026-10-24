from src.services.auth_service import register_user, login_user
from src.services.logistics_service import view_supplies, add_supply_item, create_shipment
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
        console.print("3. Logout / Switch User")
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
        elif choice == "2":
            add_supply_item()
        elif choice == "3":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


def dispatcher_menu(user):
    while True:
        console.print(f"\n[bold cyan]--- Dispatcher Dashboard ({user.user_name}) ---[/bold cyan]")
        console.print("1. View Supplies Inventory")
        console.print("2. Check Crisis Weather (Live API)")
        console.print("3. Get Smart Supply Recommendations")
        console.print("4. Create & Dispatch Shipment")
        console.print("5. Logout / Switch User")
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
            
        elif choice == "2":
            console.print("\n[bold yellow]--- Select Crisis Region ---[/bold yellow]")
            console.print("1. Riyadh")
            console.print("2. Tabuk")
            console.print("3. Jeddah")
            console.print("4. Dammam")
            console.print("5. Custom Coordinates (Manual)")
            
            reg_choice = input("Choose region (1-5): ").strip()
            
            regions_map = {
                "1": {"name": "Riyadh", "lat": 24.7136, "lon": 46.6753},
                "2": {"name": "Tabuk", "lat": 28.3972, "lon": 36.5788},
                "3": {"name": "Jeddah", "lat": 21.5433, "lon": 39.1728},
                "4": {"name": "Dammam", "lat": 26.4207, "lon": 50.0888}
            }
            
            lat, lon = None, None
            target_name = ""
            
            if reg_choice in regions_map:
                target_name = regions_map[reg_choice]["name"]
                lat = regions_map[reg_choice]["lat"]
                lon = regions_map[reg_choice]["lon"]
            elif reg_choice == "5":
                try:
                    lat = float(input("Enter latitude: ").strip())
                    lon = float(input("Enter longitude: ").strip())
                    target_name = "Custom Location"
                except ValueError:
                    console.print("[bold red]Invalid coordinates entered.[/bold red]")
                    continue
            else:
                console.print("[bold red]Invalid choice. Returning to menu.[/bold red]")
                continue
                
            console.print(f"[cyan]Fetching live weather for {target_name}...[/cyan]")
            weather = get_crisis_weather(lat, lon)
            if weather:
                console.print(f"\n[bold green]Live Weather Status ({target_name}):[/bold green]")
                console.print(f"Temperature: {weather.get('temperature')}°C")
                console.print(f"Wind Speed: {weather.get('windspeed')} km/h")
                
                if weather.get('windspeed', 0) > 30:
                    console.print("[bold red]⚠️ Warning: High wind speeds detected! Exercise caution for air/ground dispatch.[/bold red]")
                else:
                    console.print("[bold green]✨ Weather conditions are stable for dispatch.[/bold green]")
            else:
                console.print("[bold red]Could not fetch weather data at this moment.[/bold red]")
                
        elif choice == "3":
            category = input("Enter crisis category (Medical, Food, Shelter): ").strip()
            recs = get_smart_recommendations(category)
            if recs:
                console.print(f"\n[bold magenta]Smart Recommendations for '{category}':[/bold magenta]")
                display_supplies_table(recs)
            else:
                console.print("[yellow]No specific recommendations found.[/yellow]")
                
        elif choice == "4":
            shipment_id = create_shipment()
            if shipment_id:
                simulate_dispatch_progress(shipment_id)
                
        elif choice == "5":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


def general_user_menu(user):
    while True:
        console.print(f"\n[bold cyan]--- General Dashboard ({user.user_name} - {user.role}) ---[/bold cyan]")
        console.print("1. View Supplies Inventory")
        console.print("2. Logout / Switch User")
        
        choice = input("Choose an option (1-2): ").strip()
        
        if choice == "1":
            supplies = view_supplies()
            display_supplies_table(supplies)
        elif choice == "2":
            console.print("[yellow]Logging out...[/yellow]")
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


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
                else:
                    general_user_menu(current_user)
                    
        elif main_choice == "2":
            register_user()
            
        elif main_choice == "3":
            console.print("\n[bold green]Exiting program. Stay safe![/bold green]")
            break
        else:
            console.print("[bold red]Invalid choice. Please enter 1, 2, or 3.[/bold red]")

if __name__ == "__main__":
    main()