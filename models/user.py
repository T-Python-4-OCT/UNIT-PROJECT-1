import hashlib
from dataclasses import dataclass, asdict


def hash_password(password: str) -> str:
    """Return the SHA-256 hash of the password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass
class Receptionist:
    id: int
    username: str
    password_hash: str
    full_name: str

    def check_password(self, password: str) -> bool:
        return self.password_hash == hash_password(password)

    def to_dict(self) -> dict:
        return asdict(self)