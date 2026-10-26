from dataclasses import dataclass, asdict


@dataclass
class Appointment:
    id: int
    patient_id: int
    clinic_id: int
    date: str                 # "2026-10-25"
    time: str                 # "10:30"
    status: str = "booked"    # booked / checked_in / completed / cancelled

    def to_dict(self) -> dict:
        return asdict(self)