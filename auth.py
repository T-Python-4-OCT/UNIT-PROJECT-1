import hashlib
import hmac
import secrets

from data_manager import load_data, save_data


USERS_FILE = "users.json"


def hash_password(password, salt=None):
    """Hash a password securely."""
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt),
        n=16384,
        r=8,
        p=1,
        dklen=64
    )

    return {
        "salt": salt,
        "password_hash": password_hash.hex()
    }


def verify_password(password, salt, stored_hash):
    """Check whether a password matches its stored hash."""
    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt),
        n=16384,
        r=8,
        p=1,
        dklen=64
    )

    return hmac.compare_digest(
        password_hash.hex(),
        stored_hash
    )


def login(username, password):
    """Authenticate a user and return their account if valid."""
    users = load_data(USERS_FILE)

    for user in users:
        if user.get("username") != username:
            continue

        if not user.get("active", True):
            return None

        if verify_password(
            password,
            user["salt"],
            user["password_hash"]
        ):
            return user

        return None

    return None


def has_role(user, role):
    """Check whether a user has a specific role."""
    if user is None:
        return False

    return user.get("role") == role
