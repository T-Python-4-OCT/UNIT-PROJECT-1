import hashlib
import hmac
import json
import os
import secrets

import config
import storage

ADMIN_FILE = os.path.join(storage.DATA_DIR, "admin.json")


def _hash(password, salt, iterations=config.PASSWORD_HASH_ITERATIONS):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def password_is_set():
    return os.path.exists(ADMIN_FILE)


def set_password(password):
    if len(password) < config.MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters.")
    salt = secrets.token_bytes(16)
    data = {
        "salt": salt.hex(),
        "hash": _hash(password, salt).hex(),
        "iterations": config.PASSWORD_HASH_ITERATIONS,
    }
    os.makedirs(storage.DATA_DIR, exist_ok=True)
    with open(ADMIN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def verify_password(password):
    if not password_is_set():
        return False
    try:
        with open(ADMIN_FILE, encoding="utf-8") as f:
            data = json.load(f)
        salt = bytes.fromhex(data["salt"])
        stored = bytes.fromhex(data["hash"])
        iterations = int(data["iterations"])
    except (OSError, ValueError, KeyError):
        return False
    return hmac.compare_digest(_hash(password, salt, iterations), stored)