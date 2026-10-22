IRRIGATION_TYPES = ("drip", "sprinkler", "flood")


class Farm:
    """A farm with its planted crops and irrigation log."""

    def __init__(self, farm_name, city, crops=None, irrigation_log=None, last_savings=None):
        self.farm_name = farm_name
        self.city = city
        self.crops = crops if crops is not None else []
        self.irrigation_log = irrigation_log if irrigation_log is not None else []
        self.last_savings = last_savings  # latest savings estimate, or None

    def find_crop(self, crop_id):
        """Return the planted crop entry with this id, or None."""
        for crop in self.crops:
            if crop["crop_id"] == crop_id:
                return crop
        return None

    def add_crop(self, crop_id, area_m2, irrigation_type):
        if self.find_crop(crop_id):
            raise ValueError(f"'{crop_id}' is already on this farm.")
        if irrigation_type not in IRRIGATION_TYPES:
            raise ValueError(f"Irrigation type must be one of: {', '.join(IRRIGATION_TYPES)}.")
        self.crops.append({
            "crop_id": crop_id,
            "area_m2": area_m2,
            "irrigation_type": irrigation_type,
        })

    def update_crop(self, crop_id, area_m2=None, irrigation_type=None):
        crop = self.find_crop(crop_id)
        if crop is None:
            raise ValueError(f"'{crop_id}' is not on this farm.")
        if irrigation_type is not None and irrigation_type not in IRRIGATION_TYPES:
            raise ValueError(f"Irrigation type must be one of: {', '.join(IRRIGATION_TYPES)}.")
        if area_m2 is not None:
            crop["area_m2"] = area_m2
        if irrigation_type is not None:
            crop["irrigation_type"] = irrigation_type

    def remove_crop(self, crop_id):
        crop = self.find_crop(crop_id)
        if crop is None:
            raise ValueError(f"'{crop_id}' is not on this farm.")
        self.crops.remove(crop)

    def add_irrigation_log(self, crop_id, date, volume_m3):
        """Record irrigation that the farmer actually performed."""
        if self.find_crop(crop_id) is None:
            raise ValueError(f"'{crop_id}' is not on this farm.")
        self.irrigation_log.append({
            "crop_id": crop_id,
            "date": date,
            "volume_m3": volume_m3,
        })

    def total_area(self):
        return sum(crop["area_m2"] for crop in self.crops)

    def to_dict(self):
        return {
            "farm_name": self.farm_name,
            "city": self.city,
            "crops": self.crops,
            "irrigation_log": self.irrigation_log,
            "last_savings": self.last_savings,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["farm_name"],
            data["city"],
            data.get("crops", []),
            data.get("irrigation_log", []),
            data.get("last_savings"),
        )