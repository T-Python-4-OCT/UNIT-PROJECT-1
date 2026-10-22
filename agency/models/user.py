from dataclasses import asdict, dataclass, fields


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    full_name: str
    email: str
    role: str
    phone: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "User":
        known = {model_field.name for model_field in fields(User)}
        return User(**{key: value for key, value in data.items() if key in known})
