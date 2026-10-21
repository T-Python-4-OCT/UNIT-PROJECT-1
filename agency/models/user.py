"""User data model."""
from dataclasses import asdict, dataclass, fields


@dataclass
class User:
    """A customer or manager account."""
    id: int
    username: str
    password_hash: str
    full_name: str
    email: str
    role: str            # "customer" or "manager"
    phone: str = ""      # mobile number (older accounts may not have one)

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON storage."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "User":
        """Build the object from a dict loaded from JSON."""
        known = {model_field.name for model_field in fields(User)}
        return User(**{key: value for key, value in data.items() if key in known})
