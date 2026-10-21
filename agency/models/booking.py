"""Booking data model."""
from dataclasses import asdict, dataclass, fields


@dataclass
class Booking:
    """One trip booked by a customer (price, status and payment)."""
    id: int
    user_id: int
    country_id: int
    country: str         # snapshot, stays correct even if the country is deleted
    city: str
    travel_date: str
    days: int
    travelers: int
    style: str
    total_price: int
    breakdown: dict
    status: str          # pending / confirmed / completed / cancelled
    created_at: str
    paid: bool = False
    payment_method: str = ""
    reference: str = ""
    promo_code: str = ""     # occasion code used at booking time (the discount is inside breakdown)

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON storage."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Booking":
        """Build the object from a dict loaded from JSON."""
        known = {model_field.name for model_field in fields(Booking)}
        return Booking(**{key: value for key, value in data.items() if key in known})
