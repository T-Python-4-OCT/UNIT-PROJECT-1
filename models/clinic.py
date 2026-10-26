from dataclasses import dataclass, field, asdict


@dataclass
class Clinic:
    id: int
    name: str                 # e.g. "Cardiology"
    doctor: str               # e.g. "Dr. Ahmed Ali"
    fee: float = 100.0
    # {"sunday": ["09:00", "14:00"], ...}
    working_hours: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)