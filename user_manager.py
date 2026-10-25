from data_manager import load_data, save_data
from auth import hash_password


USERS_FILE = "users.json"

VALID_ROLES = ["admin", "member"]


def create_user(username, password, role="member"):
    """Create a new user account."""

    username = username.strip()

    if not username:
        return False, "Username cannot be empty."

    if not username[0].isascii() or not username[0].isalpha():
        return False, "Username must start with an English letter."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    if role not in VALID_ROLES:
        return False, "Invalid role."

    users = load_data(USERS_FILE)

    for user in users:
        if user.get("username", "").lower() == username.lower():
            return False, "Username already exists."

    password_data = hash_password(password)

    new_user = {
        "username": username,
        "role": role,
        "active": True,
        "salt": password_data["salt"],
        "password_hash": password_data["password_hash"]
    }

    users.append(new_user)
    save_data(USERS_FILE, users)

    return True, "User created successfully."


def get_all_users():
    """Return all users without exposing password data."""

    users = load_data(USERS_FILE)

    public_users = []

    for user in users:
        public_users.append({
            "username": user.get("username"),
            "role": user.get("role"),
            "active": user.get("active", True)
        })

    return public_users


def set_user_status(username, active):
    """Activate or deactivate a user account."""

    users = load_data(USERS_FILE)

    for user in users:
        if user.get("username", "").lower() == username.lower():
            user["active"] = active
            save_data(USERS_FILE, users)
            return True, "User status updated."

    return False, "User not found."
