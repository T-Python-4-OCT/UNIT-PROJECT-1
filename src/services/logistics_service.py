import json
import os
from src.utils.display import display_supplies_table
from rich.console import Console

console = Console()

SUPPLIES_FILE = "data/supplies.json"
SHIPMENTS_FILE = "data/shipments.json"

def load_supplies():
    if not os.path.exists(SUPPLIES_FILE):
        return []
    try:
        with open(SUPPLIES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_supplies(supplies):
    os.makedirs(os.path.dirname(SUPPLIES_FILE), exist_ok=True)
    with open(SUPPLIES_FILE, "w") as f:
        json.dump(supplies, f, indent=2)

def load_shipments():
    if not os.path.exists(SHIPMENTS_FILE):
        return []
    try:
        with open(SHIPMENTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_shipments(shipments):
    os.makedirs(os.path.dirname(SHIPMENTS_FILE), exist_ok=True)
    with open(SHIPMENTS_FILE, "w") as f:
        json.dump(shipments, f, indent=2)

def view_supplies():
    return load_supplies()

def add_supply_item():
    console.print("\n[bold yellow]--- Add New Supply Item ---[/bold yellow]")
    supplies = load_supplies()
    
    item_id = f"SUPP-{len(supplies) + 1:03d}"
    name = input("Enter item name: ").strip()
    category = input("Enter category (Medical, Food, Shelter): ").strip()
    
    try:
        quantity = int(input("Enter quantity: ").strip())
        unit_weight = float(input("Enter unit weight (kg): ").strip())
    except ValueError:
        console.print("[bold red]❌ Invalid number format. Item creation cancelled.[/bold red]")
        return
        
    new_item = {
        "id": item_id,
        "name": name,
        "category": category,
        "quantity": quantity,
        "unit_weight": unit_weight
    }
    
    supplies.append(new_item)
    save_supplies(supplies)
    console.print(f"[bold green]✅ Success: Item '{name}' ({item_id}) added to inventory![/bold green]")

def create_shipment():
    console.print("\n[bold yellow]--- Create Shipment Request (Dispatcher) ---[/bold yellow]")
    supplies = load_supplies()
    
    if not supplies:
        console.print("[bold red]❌ No supplies available in inventory to ship.[/bold red]")
        return None
        
    display_supplies_table(supplies)
    
    item_id = input("Enter Supply ID to dispatch (e.g., SUPP-001 or 004): ").strip()
    
    # بحث ذكي ومطور يتجاوز أي مشاكل في المسافات أو المطابقة
    target_item = None
    for item in supplies:
        db_id = str(item.get("id", "")).strip().lower()
        clean_input = item_id.strip().lower()
        
        if db_id == clean_input or db_id.endswith(clean_input) or clean_input.endswith(db_id) or clean_input in db_id:
            target_item = item
            break
            
    if not target_item:
        console.print("[bold red]❌ Supply ID not found.[/bold red]")
        return None
        
    try:
        qty_to_ship = int(input(f"Enter quantity to ship (Available: {target_item['quantity']}): ").strip())
    except ValueError:
        console.print("[bold red]❌ Invalid quantity entered.[/bold red]")
        return None
        
    if qty_to_ship <= 0 or qty_to_ship > target_item['quantity']:
        console.print("[bold red]❌ Invalid quantity amount or exceeds available stock.[/bold red]")
        return None
        
    destination = input("Enter destination zone (Riyadh, Tabuk, Jeddah, Dammam): ").strip() or "General Zone"
    
    # خصم الكمية من المخزون فوراً
    target_item['quantity'] -= qty_to_ship
    save_supplies(supplies)
    
    # تسجيل الشحنة بحالة معلقة بانتظار الأسطول
    shipments = load_shipments()
    shipment_id = f"SHP-{len(shipments) + 101}"
    
    new_shipment = {
        "shipment_id": shipment_id,
        "item_name": target_item['name'],
        "quantity": qty_to_ship,
        "destination": destination,
        "status": "Pending Fleet Assignment",
        "vehicle": None
    }
    
    shipments.append(new_shipment)
    save_shipments(shipments)
    
    console.print(f"[bold green]✅ Shipment {shipment_id} created and sent to Fleet Officer for review & transport selection![/bold green]")
    return shipment_id

def get_pending_shipments():
    shipments = load_shipments()
    return [s for s in shipments if s.get("status") == "Pending Fleet Assignment"]

def assign_vehicle_to_shipment(shipment_id, vehicle_name):
    shipments = load_shipments()
    updated = False
    for s in shipments:
        if s.get("shipment_id") == shipment_id:
            s["vehicle"] = vehicle_name
            s["status"] = "In Transit"
            updated = True
            break
    if updated:
        save_shipments(shipments)
        return True
    return False