from src.utils.json_handler import load_json, save_json
from src.models.supply import SupplyItem
from src.models.shipment import Shipment

SUPPLIES_FILE = "data/supplies.json"
SHIPMENTS_FILE = "data/shipments.json"

def view_supplies():
    supplies_list = load_json(SUPPLIES_FILE)
    if not supplies_list:
        print("\nNo supplies available in the inventory.")
        return supplies_list

    print("\n--- Current Emergency Supplies Inventory ---")
    for item in supplies_list:
        print(f"ID: {item.get('item_id')} | Name: {item.get('name')} | Category: {item.get('category')} | Qty: {item.get('quantity')} | Weight/Unit: {item.get('unit_weight_kg')}kg")
    
    return supplies_list


def add_supply_item():
    print("\n--- Add New Supply Item (Manager Only) ---")
    name = input("Enter supply item name: ").strip()
    category = input("Enter category (Medical, Food, Shelter): ").strip()
    
    while True:
        try:
            quantity = int(input("Enter quantity: ").strip())
            unit_weight_kg = float(input("Enter unit weight in kg: ").strip())
            if quantity > 0 and unit_weight_kg > 0:
                break
            print("Quantity and weight must be greater than zero.")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    supplies_list = load_json(SUPPLIES_FILE)
    item_id = f"SUPP-{len(supplies_list) + 1:03d}"

    new_item = SupplyItem(item_id, name, category, quantity, unit_weight_kg)
    supplies_list.append(new_item.to_dict())
    save_json(SUPPLIES_FILE, supplies_list)

    print(f"Supply item '{name}' added successfully with ID ({item_id})!")


def create_shipment():
    print("\n--- Create & Dispatch Shipment (Dispatcher) ---")
    destination = input("Enter destination crisis zone: ").strip()
    
    print("\nSelect Transport Type:")
    print("1. Drone")
    print("2. Truck")
    print("3. Cargo Plane")
    
    while True:
        choice = input("Enter option (1-3): ").strip()
        if choice == "1":
            transport_type = "Drone"
            break
        elif choice == "2":
            transport_type = "Truck"
            break
        elif choice == "3":
            transport_type = "Cargo Plane"
            break
        print("Invalid transport choice. Try again.")

    shipments_list = load_json(SHIPMENTS_FILE)
    shipment_id = f"SHIP-{len(shipments_list) + 1:03d}"

    new_shipment = Shipment(shipment_id, destination, transport_type)

    supplies_list = load_json(SUPPLIES_FILE)
    if not supplies_list:
        print("Cannot add items because inventory is empty.")
        return

    while True:
        view_supplies()
        item_id_input = input("Enter Supply ID to add to shipment (or type 'done' to finish): ").strip()
        
        if item_id_input.lower() == 'done':
            break

        found_item = None
        for item in supplies_list:
            if item.get("item_id") == item_id_input:
                found_item = item
                break

        if not found_item:
            print("Supply ID not found. Try again.")
            continue

        try:
            qty_to_add = int(input(f"Enter quantity to add (Available: {found_item.get('quantity')}): ").strip())
            if qty_to_add <= 0 or qty_to_add > found_item.get("quantity"):
                print("Invalid quantity amount.")
                continue
        except ValueError:
            print("Please enter a valid integer.")
            continue

        new_shipment.add_item(
            item_id=found_item.get("item_id"),
            item_name=found_item.get("name"),
            quantity=qty_to_add,
            unit_weight_kg=found_item.get("unit_weight_kg")
        )

        found_item["quantity"] -= qty_to_add
        save_json(SUPPLIES_FILE, supplies_list)
        print(f"Added {qty_to_add} of {found_item.get('name')} to shipment.")

        cont = input("Add another item? (y/n): ").strip().lower()
        if cont != 'y':
            break

    if not new_shipment.items:
        print("Shipment creation cancelled because no items were added.")
        return

    shipments_list.append(new_shipment.to_dict())
    save_json(SHIPMENTS_FILE, shipments_list)
    print(f"Shipment '{shipment_id}' created successfully and saved!")