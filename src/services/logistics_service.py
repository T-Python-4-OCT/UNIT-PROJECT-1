import json
import os
from src.utils.display import display_supplies_table
from rich.console import Console
from rich.table import Table

console = Console()

SUPPLIES_FILE = "data/supplies.json"
SHIPMENTS_FILE = "data/shipments.json"
FIELD_REQUESTS_FILE = "data/field_requests.json"

def load_supplies():
    if not os.path.exists(SUPPLIES_FILE):
        return []
    try:
        with open(SUPPLIES_FILE, "r") as f:
            supplies = json.load(f)
            updated = False
            max_num = 0
            
            for item in supplies:
                for key in ["id", "item_id", "SUPP_ID", "code"]:
                    if key in item and item[key]:
                        val = str(item[key]).strip()
                        digits = "".join(filter(str.isdigit, val))
                        if digits.isdigit():
                            num = int(digits)
                            if num > max_num:
                                max_num = num
            
            normalized_supplies = []
            for item in supplies:
                item_id = ""
                for key in ["id", "item_id", "SUPP_ID", "code"]:
                    if key in item and item[key] and str(item[key]).strip():
                        item_id = str(item[key]).strip()
                        break
                
                if not item_id or item_id.lower() == "none" or not item_id.startswith("SUPP-"):
                    max_num += 1
                    item_id = f"SUPP-{max_num:03d}"
                    updated = True
                
                name = next((str(item[k]).strip() for k in ["name", "item_name", "title"] if k in item and item[k]), "Unknown Item")
                category = next((str(item[k]).strip() for k in ["category", "type"] if k in item and item[k]), "General")
                
                quantity = 0
                for k in ["quantity", "qty", "stock"]:
                    if k in item:
                        try:
                            quantity = int(item[k])
                            break
                        except ValueError:
                            pass
                
                unit_weight = 0.0
                for k in ["unit_weight", "unit_weight_kg", "weight", "kg"]:
                    if k in item:
                        try:
                            unit_weight = float(item[k])
                            break
                        except ValueError:
                            pass
                
                normalized_item = {
                    "id": item_id,
                    "item_id": item_id,
                    "name": name,
                    "category": category,
                    "quantity": quantity,
                    "unit_weight": unit_weight,
                    "unit_weight_kg": unit_weight
                }
                
                if item != normalized_item:
                    updated = True
                
                normalized_supplies.append(normalized_item)
                
            if updated:
                save_supplies(normalized_supplies)
                
            return normalized_supplies
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

def load_field_requests():
    if not os.path.exists(FIELD_REQUESTS_FILE):
        return []
    try:
        with open(FIELD_REQUESTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_field_requests(requests):
    os.makedirs(os.path.dirname(FIELD_REQUESTS_FILE), exist_ok=True)
    with open(FIELD_REQUESTS_FILE, "w") as f:
        json.dump(requests, f, indent=2)

def view_supplies():
    return load_supplies()

def display_field_requests_table(requests):
    table = Table(title="🚨 Field Supervisor Requests Dashboard", title_style="bold magenta", border_style="cyan")
    table.add_column("Request ID", style="cyan", justify="center")
    table.add_column("Item Name", style="white")
    table.add_column("Quantity", style="green", justify="right")
    table.add_column("Zone", style="yellow")
    table.add_column("Status", style="bold", justify="center")

    for r in requests:
        status = r.get('status', 'Pending')
        if status == "Pending":
            status_str = "[yellow]Pending (Awaiting Dispatch)[/yellow]"
        elif status == "In Transit" or status == "Converted":
            status_str = "[cyan]In Transit / Processed[/cyan]"
        else:
            status_str = f"[green]{status}[/green]"
            
        table.add_row(
            r.get('request_id'),
            r.get('item_name'),
            str(r.get('quantity')),
            r.get('zone'),
            status_str
        )
    console.print(table)

def add_supply_item():
    console.print("\n[bold yellow]--- Add New Supply Item ---[/bold yellow]")
    supplies = load_supplies()
    
    max_num = 0
    for item in supplies:
        db_id = str(item.get("id", ""))
        digits = "".join(filter(str.isdigit, db_id))
        if digits.isdigit():
            num = int(digits)
            if num > max_num:
                max_num = num
    item_id = f"SUPP-{max_num + 1:03d}"
    
    console.print(f"[cyan]Auto-generated Item ID: {item_id}[/cyan]")
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
        "item_id": item_id,
        "name": name,
        "category": category,
        "quantity": quantity,
        "unit_weight": unit_weight,
        "unit_weight_kg": unit_weight
    }
    
    supplies.append(new_item)
    save_supplies(supplies)
    console.print(f"[bold green]✅ Success: Item '{name}' ({item_id}) added to inventory automatically![/bold green]")

def create_field_request(zone):
    console.print("\n[bold yellow]--- Report Urgent Field Request ---[/bold yellow]")
    item_name = input("Enter required material name: ").strip()
    try:
        quantity = int(input("Enter required quantity: ").strip())
    except ValueError:
        console.print("[bold red]❌ Invalid quantity format.[/bold red]")
        return False
        
    priority = {"1": "High", "2": "Medium", "3": "Low"}.get(
        input("Priority (1=High, 2=Medium, 3=Low) [2]: ").strip() or "2", "Medium")

    requests = load_field_requests()
    req_id = f"REQ-{len(requests) + 101}"
    
    new_req = {
        "request_id": req_id,
        "item_name": item_name,
        "quantity": quantity,
        "zone": zone,
        "priority": priority,
        "status": "Pending"
    }
    
    requests.append(new_req)
    save_field_requests(requests)
    console.print(f"[bold green]✅ Urgent request {req_id} for {quantity}x '{item_name}' submitted for zone {zone} (Sent to Dispatcher)![/bold green]")
    return True

def create_shipment():
    console.print("\n[bold yellow]--- Create Shipment Request (Dispatcher) ---[/bold yellow]")
    supplies = load_supplies()
    
    if not supplies:
        console.print("[bold red]❌ No supplies available in inventory to ship.[/bold red]")
        return None
        
    display_supplies_table(supplies)
    
    item_id_input = input("Enter Supply ID to dispatch (e.g., SUPP-003 or 3): ").strip().lower()
    
    clean_input = item_id_input.strip().lower()
    input_digits = "".join(filter(str.isdigit, clean_input))
    
    target_item = None
    for item in supplies:
        db_id = str(item.get("id", "")).strip().lower()
        db_digits = "".join(filter(str.isdigit, db_id))
        
        if db_id == clean_input:
            target_item = item
            break
        if input_digits and db_digits and int(db_digits) == int(input_digits):
            target_item = item
            break
            
    if not target_item:
        console.print("[bold red]❌ Supply ID not found.[/bold red]")
        return None
        
    console.print(f"[cyan]Selected Item: {target_item['name']} (Available: {target_item['quantity']})[/cyan]")
    
    try:
        qty_to_ship = int(input(f"Enter quantity to ship: ").strip())
    except ValueError:
        console.print("[bold red]❌ Invalid quantity entered.[/bold red]")
        return None
        
    if qty_to_ship <= 0 or qty_to_ship > target_item['quantity']:
        console.print("[bold red]❌ Invalid quantity amount or exceeds available stock.[/bold red]")
        return None
        
    destination = input("Enter destination zone (Riyadh, Tabuk, Jeddah, Dammam): ").strip() or "General Zone"
    
    target_item['quantity'] -= qty_to_ship
    save_supplies(supplies)
    
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
    
    # تحديث حالة الطلبات الميدانية المرتبطة لتصبح قيد المعالجة
    requests = load_field_requests()
    for r in requests:
        if r.get('status') == "Pending" and r.get('item_name').lower() in target_item['name'].lower():
            r['status'] = "In Transit / Processed"
    save_field_requests(requests)
    
    console.print(f"[bold green]✅ Shipment {shipment_id} created successfully for '{target_item['name']}' and sent to Fleet Officer![/bold green]")
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
            s["status"] = "Completed & In Transit"
            updated = True
            break
            
    if updated:
        save_shipments(shipments)
        
        requests = load_field_requests()
        for r in requests:
            if r.get('status') != "Completed":
                r['status'] = "Completed (Dispatched)"
        save_field_requests(requests)
        
        return True
    return False