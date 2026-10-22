# Simplifications (adjust them if you find better values from FAO tables):
# - Only 80% of the rain is counted as useful for the plants.
# - Irrigation efficiency depends on the irrigation method.
EFFECTIVE_RAIN_FACTOR = 0.8
IRRIGATION_EFFICIENCY = {
    "drip": 0.90,
    "sprinkler": 0.75,
    "flood": 0.60,
}
DEFAULT_EFFICIENCY = 0.75


def crop_water_use_mm(et0_mm, kc):
    """Water the crop uses in one day (mm): ET0 x Kc."""
    return et0_mm * kc


def effective_rain_mm(rain_mm):
    """The part of the rain that the plants can actually use (mm)."""
    return rain_mm * EFFECTIVE_RAIN_FACTOR


def daily_requirement_mm(et0_mm, kc, rain_mm):
    """Water the crop needs today (mm): ET0 x Kc - effective rain (never below 0)."""
    return max(0, crop_water_use_mm(et0_mm, kc) - effective_rain_mm(rain_mm))


def update_deficit_mm(deficit_mm, et0_mm, kc, rain_mm):
    """Add today's water use to the running deficit and subtract useful rain."""
    return max(0, deficit_mm + crop_water_use_mm(et0_mm, kc) - effective_rain_mm(rain_mm))


def irrigation_volume_m3(depth_mm, area_m2, irrigation_type):
    """Water to pump (m3) to apply `depth_mm` over `area_m2`, including losses.

    1 mm of water over 1 m2 equals 1 liter, so mm x m2 / 1000 gives m3.
    """
    efficiency = IRRIGATION_EFFICIENCY.get(irrigation_type, DEFAULT_EFFICIENCY)
    return depth_mm * area_m2 / 1000 / efficiency