from src.utils.json_handler import load_json, save_json
from src.models.user import Dispatcher, Manager, FieldSupervisor, FleetOfficer

USERS_FILE = "data/users.json"

def register_user():
    print("\n--- Register New User ---")
    user_name = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    
    while True:
        print("\nSelect User Role:")
        print("1. Dispatcher")
        print("2. Manager")
        print("3. Field Supervisor")
        print("4. Fleet Officer")
        
        choice = input("Enter option (1-4): ").strip()
        
        if choice == "1":
            role = "dispatcher"
            break
        elif choice == "2":
            role = "manager"
            break
        elif choice == "3":
            role = "field_supervisor"
            break
        elif choice == "4":
            role = "fleet_officer"
            break
        else:
            print("Invalid choice, please try again.")

    users_list = load_json(USERS_FILE)
    
    for user_data in users_list:
        if user_data.get("user_name") == user_name:
            print(f"Error: Username '{user_name}' already exists!")
            return None

    if role == "dispatcher":
        new_user = Dispatcher(user_name, email)
    elif role == "manager":
        new_user = Manager(user_name, email)
    elif role == "field_supervisor":
        crisis_zone = input("Enter assigned crisis zone: ").strip()
        new_user = FieldSupervisor(user_name, email, crisis_zone)
    elif role == "fleet_officer":
        new_user = FleetOfficer(user_name, email)

    users_list.append(new_user.to_dict())
    save_json(USERS_FILE, users_list)
    
    print(f"User '{user_name}' registered successfully with role ({role})!")
    return new_user


def login_user():
    print("\n--- User Login ---")
    user_name = input("Enter username: ").strip()
    
    users_list = load_json(USERS_FILE)
    
    for user_data in users_list:
        if user_data.get("user_name") == user_name:
            print(f"Welcome back, {user_name}! Login successful.")
            role = user_data.get("role")
            
            if role == "dispatcher":
                return Dispatcher(user_name, user_data.get("email"))
            elif role == "manager":
                return Manager(user_name, user_data.get("email"), user_data.get("department", "Operations"))
            elif role == "field_supervisor":
                return FieldSupervisor(user_name, user_data.get("email"), user_data.get("assigned_crisis_zone", "General"))
            elif role == "fleet_officer":
                return FleetOfficer(user_name, user_data.get("email"), user_data.get("specialty", "Drones"))
            
            return user_data

    print(f"No user found with the name '{user_name}'.")
    return None