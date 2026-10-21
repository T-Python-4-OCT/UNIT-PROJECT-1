class Crop:
    """A crop type in the database (managed by the Manager)."""

    def __init__(self, crop_id, name, kc, min_temp, irrigation_efficiency):
        self.crop_id = crop_id
        self.name = name
        self.kc = kc
        self.min_temp = min_temp
        self.irrigation_efficiency = irrigation_efficiency

    def to_dict(self):
        """Return the crop data as a dictionary (the id is used as the JSON key)."""
        return {
            "name": self.name,
            "kc": self.kc,
            "min_temp": self.min_temp,
            "irrigation_efficiency": self.irrigation_efficiency,
        }

    @classmethod
    def from_dict(cls, crop_id, data):
        """Build a Crop from a dictionary loaded from JSON."""
        return cls(
            crop_id,
            data["name"],
            data["kc"],
            data["min_temp"],
            data["irrigation_efficiency"],
        )

    def __str__(self):
        return f"{self.name} (Kc={self.kc}, min temp={self.min_temp}C)"