from dataclasses import asdict, dataclass, fields


# وجهة سفر: الدولة والمدينة والنوع والأسعار والمعالم وهل هي موقوفة.
@dataclass
class Country:
    id: int
    country: str
    city: str
    category: str
    flight: int
    hotel: int
    food: int
    transport: int
    activities: int
    best_season: str
    highlights: list
    suspended: bool = False

    # تحوّل الوجهة إلى قاموس عشان ينحفظ في ملف JSON.
    def to_dict(self) -> dict:
        return asdict(self)

    # تبني وجهة من قاموس مقروء من الملف.
    @staticmethod
    def from_dict(data: dict) -> "Country":
        return Country(**{model_field.name: data[model_field.name]
                          for model_field in fields(Country) if model_field.name in data})
