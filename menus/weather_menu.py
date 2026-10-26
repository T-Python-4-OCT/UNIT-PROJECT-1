from services.alerts import get_alerts
from services.scheduler import POSTPONE, build_schedule
from utils import display
from utils.ui_helpers import fetch_weather_for_farm


def show_alerts(farm, crops, days):
    display.print_title("Weather Alerts")
    alerts = get_alerts(farm, crops, days)
    if not alerts:
        display.print_success("No weather alerts for the coming week.")
        return
    for message in alerts:
        display.print_warning(message)


def view_weather(farm, crops):
    if farm is None:
        display.print_warning("Create your farm first (option 1).")
        return
    weather = fetch_weather_for_farm(farm)
    if weather is None:
        return

    display.print_title(f"Weather: {weather['location_name']}")
    current = weather["current"]
    print(f"Now: {current['temperature']} C, wind {current['wind_speed']} km/h\n")

    rows = [
        [day["date"], day["temp_max"], day["temp_min"], day["rain_mm"], day["wind_max"], day["et0_mm"]]
        for day in weather["daily"]
    ]
    display.print_table(rows, ["Date", "Max (C)", "Min (C)", "Rain (mm)", "Wind max (km/h)", "ET0 (mm)"])
    show_alerts(farm, crops, weather["daily"])


def show_irrigation_schedule(farm, crops):
    if farm is None:
        display.print_warning("Create your farm first (option 1).")
        return
    if not farm.crops:
        display.print_warning("Add at least one crop first (option 2).")
        return
    weather = fetch_weather_for_farm(farm)
    if weather is None:
        return

    schedule, skipped = build_schedule(farm, crops, weather["daily"])
    for crop_id in skipped:
        display.print_warning(f"'{crop_id}' is no longer in the crop database and was skipped.")

    display.print_title(f"Irrigation Schedule: {farm.farm_name}")
    rows = [
        [
            row["date"],
            row["crop_name"],
            round(row["need_mm"], 1),
            row["action"],
            round(row["volume_m3"], 1) if row["volume_m3"] > 0 else "-",
            row["best_time"],
        ]
        for row in schedule
    ]
    display.print_table(rows, ["Date", "Crop", "Need (mm)", "Action", "Water (m3)", "Best time"])

    total_m3 = round(sum(row["volume_m3"] for row in schedule), 1)
    postponed = sum(1 for row in schedule if row["action"] == POSTPONE)
    display.print_info(f"Total water this week: {total_m3} m3")
    if postponed:
        display.print_info(f"Irrigations postponed because of rain: {postponed}")
    show_alerts(farm, crops, weather["daily"])