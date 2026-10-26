from services.scheduler import RAIN_POSTPONE_MM

# Alert thresholds (simple assumptions that can be tuned)
HEAT_WAVE_C = 42
STRONG_WIND_KMH = 40


def format_dates(days):
    return ", ".join(day["date"] for day in days)


def check_heat_wave(days):
    hot_days = [day for day in days if day["temp_max"] >= HEAT_WAVE_C]
    if not hot_days:
        return []
    highest = max(day["temp_max"] for day in hot_days)
    return [
        f"Heat wave: up to {highest} C on {format_dates(hot_days)}. "
        "Irrigate at dawn and consider extra water for sensitive crops."
    ]


def check_strong_wind(days):
    windy_days = [day for day in days if day["wind_max"] >= STRONG_WIND_KMH]
    if not windy_days:
        return []
    strongest = max(day["wind_max"] for day in windy_days)
    return [
        f"Strong wind: up to {strongest} km/h on {format_dates(windy_days)}. "
        "Sprinkler irrigation loses a lot of water in wind; irrigate at dawn or use drip."
    ]


def check_rain(days):
    rainy_days = [day for day in days if day["rain_mm"] >= RAIN_POSTPONE_MM]
    if not rainy_days:
        return []
    total = round(sum(day["rain_mm"] for day in rainy_days), 1)
    return [
        f"Rain expected on {format_dates(rainy_days)} ({total} mm in total). "
        "Irrigation may be postponed."
    ]


def check_frost(farm, crops, days):
    """One alert per crop whose minimum temperature limit is crossed."""
    messages = []
    for farm_crop in farm.crops:
        crop = crops.get(farm_crop["crop_id"])
        if crop is None:
            continue
        cold_days = [day for day in days if day["temp_min"] < crop.min_temp]
        if cold_days:
            lowest = min(day["temp_min"] for day in cold_days)
            messages.append(
                f"Frost risk for {crop.name}: down to {lowest} C on {format_dates(cold_days)} "
                f"(limit {crop.min_temp} C). Cover the crop overnight."
            )
    return messages


def get_alerts(farm, crops, days):
    """Return a list of alert messages for the coming days (empty if all is calm)."""
    alerts = []
    alerts.extend(check_heat_wave(days))
    alerts.extend(check_frost(farm, crops, days))
    alerts.extend(check_strong_wind(days))
    alerts.extend(check_rain(days))
    return alerts