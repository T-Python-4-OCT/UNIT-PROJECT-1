from services import water_calculator

# Decision rules (simple assumptions that can be tuned)
IRRIGATION_THRESHOLD_MM = 10   # irrigate when the water deficit reaches this depth
MAX_DEFICIT_MM = 20            # never postpone beyond this deficit (crop stress)
RAIN_POSTPONE_MM = 5           # postpone if at least this much rain is coming
LOOKAHEAD_DAYS = 2             # how many days ahead to check for rain (plus today)
HIGH_WIND_KMH = 25
HOT_DAY_C = 38

WAIT = "Wait"
POSTPONE = "Postpone (rain)"
IRRIGATE = "Irrigate"


def upcoming_rain_mm(days, index):
    """Total rain forecast for today and the next LOOKAHEAD_DAYS days."""
    window = days[index:index + 1 + LOOKAHEAD_DAYS]
    return sum(day["rain_mm"] for day in window)


def decide_action(deficit_mm, rain_ahead_mm):
    if deficit_mm < IRRIGATION_THRESHOLD_MM:
        return WAIT
    if rain_ahead_mm >= RAIN_POSTPONE_MM and deficit_mm < MAX_DEFICIT_MM:
        return POSTPONE
    return IRRIGATE


def choose_best_time(day):
    """Dawn is best on windy or very hot days; otherwise dawn or evening."""
    if day["wind_max"] >= HIGH_WIND_KMH or day["temp_max"] >= HOT_DAY_C:
        return "Dawn"
    return "Dawn or evening"


def schedule_crop(crop, farm_crop, days):
    """Build the day-by-day schedule rows for one crop on the farm."""
    rows = []
    deficit_mm = 0
    for index, day in enumerate(days):
        deficit_mm = water_calculator.update_deficit_mm(deficit_mm, day["et0_mm"], crop.kc, day["rain_mm"])
        action = decide_action(deficit_mm, upcoming_rain_mm(days, index))

        volume_m3 = 0
        if action == IRRIGATE:
            volume_m3 = water_calculator.irrigation_volume_m3(
                deficit_mm, farm_crop["area_m2"], farm_crop["irrigation_type"]
            )
            deficit_mm = 0

        rows.append({
            "date": day["date"],
            "crop_id": farm_crop["crop_id"],
            "crop_name": crop.name,
            "need_mm": water_calculator.daily_requirement_mm(day["et0_mm"], crop.kc, day["rain_mm"]),
            "action": action,
            "volume_m3": volume_m3,
            "best_time": choose_best_time(day) if action == IRRIGATE else "-",
            "deficit_mm": deficit_mm,  # water still missing at the end of the day
        })
    return rows


def build_schedule(farm, crops, days):
    """Return (rows, skipped_crop_ids) for every crop on the farm."""
    rows = []
    skipped = []
    for farm_crop in farm.crops:
        crop = crops.get(farm_crop["crop_id"])
        if crop is None:
            skipped.append(farm_crop["crop_id"])
            continue
        rows.extend(schedule_crop(crop, farm_crop, days))
    rows.sort(key=lambda row: (row["date"], row["crop_name"]))
    return rows, skipped