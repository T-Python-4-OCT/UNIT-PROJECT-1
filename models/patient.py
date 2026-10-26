from dataclasses import dataclass, field, asdict


@dataclass
class Patient:
    id: int
    full_name: str
    phone: str
    age: int = 0
    blood_type: str = "Unknown"
    allergies: list = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)