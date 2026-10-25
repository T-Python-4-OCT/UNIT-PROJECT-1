import json
import os
import hashlib
from rich.console import Console

console = Console()
USERS_FILE = "data/users.json"

def hash_password(password, salt=None):
    """ عشوائيsalt توليد هاش آمن لكلمة المرور باستخدام   """
    if not salt:
        salt = os.urandom(32)  
    else:
        salt = bytes.fromhex(salt)
    
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex(), pwd_hash.hex()

def verify_password(stored_salt, stored_hash, provided_password):
    _, new_hash = hash_password(provided_password, stored_salt)
    return new_hash == stored_hash

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

def register_user():
    console.print("\n[bold yellow]--- Register New User ---[/bold yellow]")
    username = input("Enter username: ").strip()
    
    users = load_users()
    if any(u.get("user_name").lower() == username.lower() for u in users):
        console.print("[bold red]❌ Username already exists. Choose another one.[/bold red]")
        return False
        
    password = input("Enter password: ").strip()
    if not password:
        console.print("[bold red]❌ Password cannot be empty.[/bold red]")
        return False
        
    email = input("Enter email: ").strip()
    
    console.print("\nSelect Role:")
    console.print("1. Manager")
    console.print("2. Dispatcher")
    console.print("3. Field Supervisor")
    console.print("4. Fleet Officer")
    console.print("5. General User")
    
    role_choice = input("Choose role (1-5): ").strip()
    role_map = {
        "1": "manager",
        "2": "dispatcher",
        "3": "field_supervisor",
        "4": "fleet_officer",
        "5": "general"
    }
    role = role_map.get(role_choice, "general")
    
    salt, password_hash = hash_password(password)
    
    extra_field = {}
    if role == "field_supervisor":
        zone = input("Enter assigned crisis zone (Riyadh, Tabuk, Jeddah, Dammam): ").strip() or "General Zone"
        extra_field["crisis_zone"] = zone
    elif role == "fleet_officer":
        specialty = input("Enter fleet specialty (Ground, Air, Heavy): ").strip() or "Logistics"
        extra_field["specialty"] = specialty

    new_user = {
        "user_name": username,
        "email": email,
        "role": role,
        "salt": salt,
        "password_hash": password_hash,
        **extra_field
    }
    
    users.append(new_user)
    save_users(users)
    console.print(f"[bold green]✅ User '{username}' registered successfully with secure hashed password![/bold green]")
    return True

def login_user():
    console.print("\n[bold yellow]--- System Login ---[/bold yellow]")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    users = load_users()
    for user in users:
        if user.get("user_name", "").lower() == username.lower():
            stored_salt = user.get("salt")
            stored_hash = user.get("password_hash")
            
            if not stored_salt or not stored_hash:
                if user.get("password") == password:
                    console.print(f"[bold green]✅ Welcome back, {username}! (Legacy login)[/bold green]")
                    return user
            
            if stored_salt and stored_hash and verify_password(stored_salt, stored_hash, password):
                console.print(f"[bold green]✅ Welcome back, {username}! Login successful.[/bold green]")
                return user
                
    console.print("[bold red]❌ Invalid username or password.[/bold red]")
    return None