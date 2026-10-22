from services import water_calculator


def traditional_volume_m3(crop, farm_crop, days):
    """Traditional fixed schedule: irrigate every day to replace the full crop
    water use (ET0 x Kc), without looking at the rain."""
    return sum(
        water_calculator.irrigation_volume_m3(
            water_calculator.crop_water_use_mm(day["et0_mm"], crop.kc),
            farm_crop["area_m2"],
            farm_crop["irrigation_type"],
        )
        for day in days
    )


def smart_volume_m3(farm_crop, crop_rows):
    """Smart schedule: water already scheduled, plus the deficit still waiting at
    the end of the week (so the comparison with the traditional schedule is fair)."""
    scheduled = sum(row["volume_m3"] for row in crop_rows)
    remaining = 0
    if crop_rows:
        remaining = water_calculator.irrigation_volume_m3(
            crop_rows[-1]["deficit_mm"], farm_crop["area_m2"], farm_crop["irrigation_type"]
        )
    return scheduled + remaining


def build_savings_report(farm, crops, days, schedule_rows):
    """One row per crop: traditional vs smart water use for the forecast week."""
    report = []
    for farm_crop in farm.crops:
        crop = crops.get(farm_crop["crop_id"])
        if crop is None:
            continue
        crop_rows = [row for row in schedule_rows if row["crop_id"] == farm_crop["crop_id"]]
        traditional = traditional_volume_m3(crop, farm_crop, days)
        smart = smart_volume_m3(farm_crop, crop_rows)
        saved = max(0, traditional - smart)
        report.append({
            "crop_name": crop.name,
            "traditional_m3": traditional,
            "smart_m3": smart,
            "saved_m3": saved,
            "saved_percent": saved / traditional * 100 if traditional > 0 else 0,
        })
    return report


def summarize_savings(report, water_price):
    """Add up the report rows and convert the saved water to money."""
    traditional = sum(row["traditional_m3"] for row in report)
    smart = sum(row["smart_m3"] for row in report)
    saved = sum(row["saved_m3"] for row in report)
    return {
        "traditional_m3": traditional,
        "smart_m3": smart,
        "saved_m3": saved,
        "saved_percent": saved / traditional * 100 if traditional > 0 else 0,
        "saved_cost": saved * water_price,
    }


def get_logged_usage(farm, crops, water_price):
    """Total water the farmer actually logged, per crop."""
    totals = {}
    for entry in farm.irrigation_log:
        totals[entry["crop_id"]] = totals.get(entry["crop_id"], 0) + entry["volume_m3"]
    usage = []
    for crop_id, volume_m3 in totals.items():
        crop = crops.get(crop_id)
        usage.append({
            "crop_name": crop.name if crop else crop_id,
            "volume_m3": volume_m3,
            "cost": volume_m3 * water_price,
        })
    return usage