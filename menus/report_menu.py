from datetime import date

from services.reports import build_savings_report, get_logged_usage, summarize_savings
from services.scheduler import build_schedule
from utils import display, validators
from utils.file_handler import load_settings, save_farm
from utils.ui_helpers import choose_farm_crop, fetch_weather_for_farm, get_crop_name


def log_irrigation(farm, crops):
    if farm is None:
        display.print_warning("Create your farm first (option 1).")
        return
    crop_id = choose_farm_crop(farm, crops, "log")
    if crop_id is None:
        return
    volume_m3 = validators.get_positive_number("Water used (m3): ")
    log_date = validators.get_date("Date (YYYY-MM-DD, press Enter for today): ")
    try:
        farm.add_irrigation_log(crop_id, log_date, volume_m3)
    except ValueError as error:
        display.print_error(str(error))
        return
    save_farm(farm)
    display.print_success(f"Logged {volume_m3} m3 for {get_crop_name(crops, crop_id)} on {log_date}.")


def show_savings_report(farm, crops):
    if farm is None:
        display.print_warning("Create your farm first (option 1).")
        return
    if not farm.crops:
        display.print_warning("Add at least one crop first (option 2).")
        return
    weather = fetch_weather_for_farm(farm)
    if weather is None:
        return

    water_price = load_settings()["water_price_per_m3"]
    schedule, _ = build_schedule(farm, crops, weather["daily"])
    report = build_savings_report(farm, crops, weather["daily"], schedule)
    summary = summarize_savings(report, water_price)

    farm.last_savings = {
        "date": date.today().isoformat(),
        "saved_m3": round(summary["saved_m3"], 1),
        "saved_percent": round(summary["saved_percent"]),
    }
    save_farm(farm)

    display.print_title(f"Savings Report (next 7 days): {farm.farm_name}")
    rows = [
        [
            row["crop_name"],
            round(row["traditional_m3"], 1),
            round(row["smart_m3"], 1),
            round(row["saved_m3"], 1),
            f"{round(row['saved_percent'])}%",
        ]
        for row in report
    ]
    rows.append([
        "TOTAL",
        round(summary["traditional_m3"], 1),
        round(summary["smart_m3"], 1),
        round(summary["saved_m3"], 1),
        f"{round(summary['saved_percent'])}%",
    ])
    display.print_table(rows, ["Crop", "Traditional (m3)", "Smart (m3)", "Saved (m3)", "Saved"])

    used_percent = 100 - summary["saved_percent"] if summary["traditional_m3"] > 0 else 0
    print(f"Smart vs traditional: {display.usage_bar(used_percent)}")
    display.print_info(
        f"Estimated saving: {round(summary['saved_m3'], 1)} m3 "
        f"= {round(summary['saved_cost'], 2)} SAR (at {water_price} SAR per m3)"
    )
    display.print_info("Traditional = fixed daily irrigation that ignores rain. Smart = schedule from the forecast.")

    logged = get_logged_usage(farm, crops, water_price)
    display.print_title("Irrigation You Logged")
    if not logged:
        display.print_info("Nothing logged yet. Use option 5 after you irrigate.")
        return
    rows = [[item["crop_name"], round(item["volume_m3"], 1), round(item["cost"], 2)] for item in logged]
    display.print_table(rows, ["Crop", "Logged (m3)", "Cost (SAR)"])