import hashlib
import hmac
import secrets
from utils.file_handler import load_manager_auth, save_manager_auth

MIN_PASSWORD_LENGTH = 6
HASH_ITERATIONS = 200_000


def hash_password(password, salt=None):
    """Return (salt, hash) for a password. A new random salt is made if none is given."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), HASH_ITERATIONS
    )
    return salt, digest.hex()


def verify_password(password, salt, stored_hash):
    _, new_hash = hash_password(password, salt)
    return hmac.compare_digest(new_hash, stored_hash)  # safe comparison


def has_manager_password():
    data = load_manager_auth()
    return "salt" in data and "hash" in data


def set_manager_password(password):
    """Save only the salt and the hash. The password itself is never stored."""
    salt, hashed = hash_password(password)
    save_manager_auth({"salt": salt, "hash": hashed})


def check_manager_password(password):
    if not has_manager_password():
        return False
    data = load_manager_auth()
    try:
        return verify_password(password, data["salt"], data["hash"])
    except ValueError:  # the file was edited by hand and is no longer valid
        return False