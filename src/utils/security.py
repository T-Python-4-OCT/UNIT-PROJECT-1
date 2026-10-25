"""Password hashing with the standard library only (no extra packages).

Stored format:  scrypt$<N>$<r>$<p>$<salt_hex>$<hash_hex>
scrypt is a deliberately slow, memory-hard hash, and every password gets its
own random salt, so two users with the same password get different hashes.
"""
import hashlib
import hmac
import os

PREFIX = "scrypt"
N, R, P = 2 ** 14, 8, 1      # cost parameters (higher = slower = harder to brute-force)
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = os.urandom(SALT_BYTES)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=N, r=R, p=P)
    return f"{PREFIX}${N}${R}${P}${salt.hex()}${digest.hex()}"


def is_hashed(stored: str) -> bool:
    return isinstance(stored, str) and stored.startswith(PREFIX + "$")


def verify_password(password: str, stored: str) -> bool:
    """Check a typed password against a stored value.

    Old accounts may still hold plain text; those are compared in constant time
    so the caller can upgrade them to a hash after a successful login.
    """
    if not isinstance(stored, str):
        return False
    if not is_hashed(stored):
        return hmac.compare_digest(password.encode("utf-8"), stored.encode("utf-8"))
    try:
        _, n, r, p, salt_hex, hash_hex = stored.split("$")
        digest = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt_hex),
                                n=int(n), r=int(r), p=int(p))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest, bytes.fromhex(hash_hex))