from dataclasses import asdict, dataclass, fields


@dataclass
class Booking:
    id: int
    user_id: int
    country_id: int
    country: str
    city: str
    travel_date: str
    days: int
    travelers: int
    style: str
    total_price: int
    breakdown: dict
    status: str
    created_at: str
    paid: bool = False
    payment_method: str = ""
    reference: str = ""
    promo_code: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Booking":
        known = {model_field.name for model_field in fields(Booking)}
        return Booking(**{key: value for key, value in data.items() if key in known})
