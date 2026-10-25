import getpass
import hmac
import json
import os
from dotenv import load_dotenv
from src.utils import display as ui
from src.utils.security import hash_password, is_hashed, verify_password
from src.models.user import Manager, Dispatcher, FieldSupervisor, FleetOfficer, User

load_dotenv()

USERS_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def migrate_passwords():
    """One-time upgrade: turn any plain-text passwords in users.json into hashes."""
    users = load_users()
    changed = False
    for u in users:
        if u.get("password") and not is_hashed(u["password"]):
            u["password"] = hash_password(u["password"])
            changed = True
    if changed:
        save_users(users)
    return changed

def register_user():
    print("\n--- Register New User ---")
    user_name = input("Enter username: ").strip()
    
    users = load_users()
    if any(u.get("user_name") == user_name for u in users):
        print("❌ Username already exists! Try logging in or use another username.")
        return None

    email = input("Enter email: ").strip()
    password = getpass.getpass("Enter password: ").strip()
    
    print("\nSelect Role:")
    print("1. Manager")
    print("2. Dispatcher")
    print("3. Field Supervisor")
    print("4. Fleet Officer")
    print("5. General User")
    
    role_choice = input("Choose role (1-5): ").strip()
    
    role_map = {
        "1": "manager",
        "2": "dispatcher",
        "3": "field_supervisor",
        "4": "fleet_officer",
        "5": "general"
    }
    
    role = role_map.get(role_choice, "general")
    
    extra_field = {}
    if role == "manager":
        extra_field["department"] = input("Enter department (e.g., Operations): ").strip() or "Operations"
    elif role == "field_supervisor":
        extra_field["crisis_zone"] = input("Enter assigned crisis zone: ").strip() or "General Zone"
    elif role == "fleet_officer":
        extra_field["specialty"] = input("Enter fleet specialty (e.g., Drones, Heavy Vehicles): ").strip() or "General Fleet"

    user_data = {
        "user_name": user_name,
        "email": email,
        "password": hash_password(password),
        "role": role,
        **extra_field
    }

    users.append(user_data)
    save_users(users)
    print(f"✅ User '{user_name}' registered successfully as {role}!")
    return user_data

def login_user():
    ui.clear()
    ui.display_header()
    ui.login_panel()
    user_name = ui.ask("Username:")
    password = getpass.getpass("Password: ").strip()

    # 1. التحقق أولاً من حساب المدير من ملف .env
    admin_env_user = os.getenv("ADMIN_USERNAME")
    admin_env_pass = os.getenv("ADMIN_PASSWORD") or os.getenv("ADMIN_DEFAULT_PASSWORD")

    if (admin_env_user and admin_env_pass
            and user_name == admin_env_user
            and hmac.compare_digest(password.encode(), admin_env_pass.encode())):
        print(f"✨ Welcome back, System Admin '{user_name}'! Login successful.")
        return Manager(user_name, "admin@system.com", "Executive Operations")

    # 2. التحقق من بقية المستخدمين المسجلين في ملف users.json
    users = load_users()
    for user_data in users:
        if user_data.get("user_name") == user_name and verify_password(password, user_data.get("password")):
            print(f"✨ Welcome back, {user_name}! Login successful.")
            role = user_data.get("role")
            
            if role == "manager":
                return Manager(user_name, user_data.get("email"), user_data.get("department", "Operations"))
            elif role == "dispatcher":
                return Dispatcher(user_name, user_data.get("email"))
            elif role == "field_supervisor":
                return FieldSupervisor(user_name, user_data.get("email"), user_data.get("crisis_zone", "General Zone"))
            elif role == "fleet_officer":
                return FleetOfficer(user_name, user_data.get("email"), user_data.get("specialty", "General Fleet"))
            else:
                return User(user_name, user_data.get("email"), role="general")

    print("❌ Invalid username or password.")
    return None