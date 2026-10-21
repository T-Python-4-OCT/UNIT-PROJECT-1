"""Destination data model."""
from dataclasses import asdict, dataclass, fields


@dataclass
class Country:
    """A destination (country and its most famous city) with estimated prices."""
    id: int
    country: str
    city: str            # most famous city
    category: str        # city / beach / culture / adventure
    flight: int          # round trip from Riyadh, per person
    hotel: int           # per night, per person
    food: int            # per day, per person
    transport: int       # per day, per person
    activities: int      # per day, per person
    best_season: str
    highlights: list
    suspended: bool = False  # manager paused this trip until further notice

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON storage."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Country":
        """Build the object from a dict loaded from JSON (old files without 'suspended' still work)."""
        return Country(**{model_field.name: data[model_field.name]
                          for model_field in fields(Country) if model_field.name in data})
