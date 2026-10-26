import hmac
import os

from dotenv import load_dotenv

from src import config
from src.models.user import Manager, Dispatcher, FieldSupervisor, FleetOfficer, User
from src.utils import display as ui
from src.utils.json_handler import load_json, save_json
from src.utils.security import (hash_password, is_hashed, is_valid_email,
                                password_problems, verify_password)

load_dotenv()


def load_users():
    return load_json(config.data_path(config.USERS_FILE))


def save_users(users):
    save_json(config.data_path(config.USERS_FILE), users)


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


def create_user(user_name, email, password, role, extra=""):
    """Validate and store a new account. Returns (ok, message). No prompts here."""
    user_name = " ".join(str(user_name).split())
    if not user_name:
        return False, "Username can't be empty."
    if not is_valid_email(email):
        return False, "Invalid email format."
    problems = password_problems(password)
    if problems:
        return False, "Password must contain " + ", ".join(problems) + "."
    if role not in [key for _, key in config.ROLES]:
        return False, "Unknown role."
    users = load_users()
    if any(u.get("user_name") == user_name for u in users):
        return False, "Username already exists."

    data = {"user_name": user_name, "email": email, "password": hash_password(password), "role": role}
    extra = " ".join(str(extra).split())
    if role == "manager":
        data["department"] = extra or "Operations"
    elif role == "field_supervisor":
        data["crisis_zone"] = extra or "General Zone"
    elif role == "fleet_officer":
        data["specialty"] = extra or "General Fleet"
    users.append(data)
    save_users(users)
    return True, f"User '{user_name}' registered successfully as {role}!"


def register_user(allowed_roles=None):
    """Interactive registration. `allowed_roles` is a list of (label, key);
    the public form omits Manager/Dispatcher (a manager creates those)."""
    roles = allowed_roles or config.PUBLIC_ROLES
    ui.heading("📝", "Register New User", color=None)

    users = load_users()
    user_name = ui.ask("Enter username (leave empty to cancel):")
    if not user_name:
        print("Registration cancelled.")
        return None
    if any(u.get("user_name") == user_name for u in users):
        ui.error("Username already exists! Try logging in or use another username.")
        return None

    while True:
        email = ui.ask("Enter email (leave empty to cancel):")
        if not email:
            print("Registration cancelled.")
            return None
        if is_valid_email(email):
            break
        ui.error("Invalid email format. Example: name@example.com")

    ui.password_rules_notice()
    while True:
        password = ui.ask_password("Enter password:").strip()
        problems = password_problems(password)
        if problems:
            ui.error("Password must contain " + ", ".join(problems) + ".")
            continue
        if ui.ask_password("Confirm password:").strip() != password:
            ui.error("Passwords don't match. Try again.")
            continue
        break

    idx = ui.select("Select Role", [label for label, _ in roles], prompt="Choose role")
    role = roles[idx][1] if idx >= 0 else "general"

    extra = ""
    if role == "manager":
        extra = ui.ask("Enter department (e.g., Operations):")
    elif role == "field_supervisor":
        extra = ui.ask("Enter assigned crisis zone:")
    elif role == "fleet_officer":
        extra = ui.ask("Enter fleet specialty (e.g., Drones, Heavy Vehicles):")

    ok, msg = create_user(user_name, email, password, role, extra)
    (ui.ok if ok else ui.error)(msg)
    return ok


def _build_user(data):
    name, email = data["user_name"], data.get("email")
    role = data.get("role")
    if role == "manager":
        return Manager(name, email, data.get("department", "Operations"))
    if role == "dispatcher":
        return Dispatcher(name, email)
    if role == "field_supervisor":
        return FieldSupervisor(name, email, data.get("crisis_zone", "General Zone"))
    if role == "fleet_officer":
        return FleetOfficer(name, email, data.get("specialty", "General Fleet"))
    return User(name, email, role="general")


def authenticate(user_name, password):
    """Returns a user object when the credentials are right, otherwise None."""
    admin_user = os.getenv("ADMIN_USERNAME")
    admin_pass = os.getenv("ADMIN_PASSWORD") or os.getenv("ADMIN_DEFAULT_PASSWORD")
    if (admin_user and admin_pass and user_name == admin_user
            and hmac.compare_digest(password.encode(), admin_pass.encode())):
        return Manager(user_name, "admin@system.com", "Executive Operations")

    for data in load_users():
        if data.get("user_name") == user_name and verify_password(password, data.get("password")):
            return _build_user(data)
    return None


def login_user():
    ui.clear()
    ui.display_header()
    ui.login_panel()
    user_name = ui.ask("Username:")
    password = ui.ask_password("Password:").strip()

    user = authenticate(user_name, password)
    if user:
        print(f"✨ Welcome back, {user_name}! Login successful.")
        return user
    ui.error("Invalid username or password.")
    return None