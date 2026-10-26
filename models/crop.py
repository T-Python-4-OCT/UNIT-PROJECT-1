import re


def make_crop_id(name):
    """Turn a crop name into an id: 'Date Palm' -> 'date_palm'. Returns '' if impossible."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


class Crop:
    """A crop type in the database (managed by the Manager)."""

    def __init__(self, crop_id, name, kc, min_temp):
        self.crop_id = crop_id
        self.name = name
        self.kc = kc
        self.min_temp = min_temp

    def to_dict(self):
        """Return the crop data as a dictionary (the id is used as the JSON key)."""
        return {
            "name": self.name,
            "kc": self.kc,
            "min_temp": self.min_temp,
        }

    @classmethod
    def from_dict(cls, crop_id, data):
        """Build a Crop from a dictionary loaded from JSON."""
        return cls(crop_id, data["name"], data["kc"], data["min_temp"])

    def __str__(self):
        return f"{self.name} (Kc={self.kc}, min temp={self.min_temp}C)"