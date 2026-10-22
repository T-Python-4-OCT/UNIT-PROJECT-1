from models.farm import Farm, IRRIGATION_TYPES
from services.alerts import get_alerts
from services.reports import build_savings_report, get_logged_usage, summarize_savings
from services.scheduler import POSTPONE, build_schedule
from services.weather import WeatherError, get_weather
from utils import display, validators
from utils.file_handler import load_crops, load_farm, load_settings, save_farm

MAIN_MENU = [
    ("1", "Manage Farm"),
    ("2", "Manage Crops"),
    ("3", "View Weather"),
    ("4", "Get Irrigation Schedule"),
    ("5", "Log Irrigation"),
    ("6", "View Savings Report"),
    ("7", "Manager Panel"),
    ("8", "Exit"),
]
COMING_SOON = ("7",)


# ---------- Helpers ----------

def print_menu(title, options):
    display.print_title(title)
    for number, label in options:
        print(f"{number}. {label}")


def get_crop_name(crops, crop_id):
    """Return the readable crop name, or the id if the crop is not in the database."""
    crop = crops.get(crop_id)
    return crop.name if crop else crop_id


def show_database_crops(crop_list):
    rows = [
        [index, crop.name, crop.kc, crop.min_temp, crop.irrigation_efficiency]
        for index, crop in enumerate(crop_list, start=1)
    ]
    display.print_table(rows, ["#", "Crop", "Kc", "Min Temp (C)", "Efficiency"])


def show_farm_crops(farm, crops):
    rows = [
        [index, get_crop_name(crops, item["crop_id"]), item["area_m2"], item["irrigation_type"]]
        for index, item in enumerate(farm.crops, start=1)
    ]
    display.print_table(rows, ["#", "Crop", "Area (m2)", "Irrigation"])


def choose_irrigation_type():
    for number, irrigation_type in enumerate(IRRIGATION_TYPES, start=1):
        print(f"{number}. {irrigation_type.capitalize()}")
    index = validators.get_number_in_range("Choose irrigation type: ", 1, len(IRRIGATION_TYPES))
    return IRRIGATION_TYPES[index - 1]


def choose_farm_crop(farm, crops, action):
    """Let the user pick one of the crops already on the farm. Return its id or None."""
    if not farm.crops:
        display.print_warning("Your farm has no crops yet.")
        return None
    show_farm_crops(farm, crops)
    index = validators.get_number_in_range(f"Enter the number of the crop to {action}: ", 1, len(farm.crops))
    return farm.crops[index - 1]["crop_id"]


# ---------- Manage Farm ----------

def show_farm(farm):
    display.print_title(f"Farm: {farm.farm_name}")
    print(f"City: {farm.city}")
    print(f"Crops: {len(farm.crops)}")
    print(f"Total area: {farm.total_area()} m2")


def create_or_edit_farm(farm):
    """Create a new farm, or change the name and city of the existing one."""
    if farm is None:
        farm_name = validators.get_text("Farm name: ")
        city = validators.get_text("City: ")
        farm = Farm(farm_name, city)
        display.print_success("Farm created.")
    else:
        farm.farm_name = validators.get_text(f"New farm name (current: {farm.farm_name}): ")
        farm.city = validators.get_text(f"New city (current: {farm.city}): ")
        display.print_success("Farm updated.")
    save_farm(farm)
    return farm


def manage_farm(farm):
    options = [("1", "View farm details"), ("2", "Create or edit farm"), ("0", "Back")]
    while True:
        print_menu("Manage Farm", options)
        choice = validators.get_menu_choice("Enter your choice: ", ["1", "2", "0"])
        if choice == "1":
            if farm is None:
                display.print_warning("No farm yet. Create one first.")
            else:
                show_farm(farm)
        elif choice == "2":
            farm = create_or_edit_farm(farm)
        else:
            return farm


# ---------- Manage Crops ----------

def add_crop(farm, crops):
    available = [crop for crop in crops.values() if farm.find_crop(crop.crop_id) is None]
    if not available:
        display.print_warning("All available crops are already on your farm.")
        return
    show_database_crops(available)
    index = validators.get_number_in_range("Enter the number of the crop to add: ", 1, len(available))
    crop = available[index - 1]
    area_m2 = validators.get_positive_number("Area in m2: ")
    irrigation_type = choose_irrigation_type()
    try:
        farm.add_crop(crop.crop_id, area_m2, irrigation_type)
    except ValueError as error:
        display.print_error(str(error))
        return
    save_farm(farm)
    display.print_success(f"{crop.name} added successfully.")


def edit_crop(farm, crops):
    crop_id = choose_farm_crop(farm, crops, "edit")
    if crop_id is None:
        return
    crop_name = get_crop_name(crops, crop_id)
    area_m2 = validators.get_positive_number("New area in m2 (press Enter to keep current): ", allow_blank=True)
    irrigation_type = None
    if validators.confirm("Change the irrigation type?"):
        irrigation_type = choose_irrigation_type()
    if area_m2 is None and irrigation_type is None:
        display.print_info("Nothing was changed.")
        return
    try:
        farm.update_crop(crop_id, area_m2, irrigation_type)
    except ValueError as error:
        display.print_error(str(error))
        return
    save_farm(farm)
    display.print_success(f"{crop_name} updated successfully.")


def delete_crop(farm, crops):
    crop_id = choose_farm_crop(farm, crops, "delete")
    if crop_id is None:
        return
    crop_name = get_crop_name(crops, crop_id)
    if not validators.confirm(f"Delete {crop_name} from your farm?"):
        display.print_info("Deletion cancelled.")
        return
    try:
        farm.remove_crop(crop_id)
    except ValueError as error:
        display.print_error(str(error))
        return
    save_farm(farm)
    display.print_success(f"{crop_name} deleted.")


def search_crops(crops):
    keyword = validators.get_text("Search crop by name: ").lower()
    results = [crop for crop in crops.values() if keyword in crop.name.lower()]
    if not results:
        display.print_warning(f"No crops found for '{keyword}'.")
        return
    show_database_crops(results)


def manage_crops(farm, crops):
    if farm is None:
        display.print_warning("Create your farm first (option 1).")
        return
    options = [
        ("1", "List my crops"),
        ("2", "Add crop"),
        ("3", "Edit crop"),
        ("4", "Delete crop"),
        ("5", "Search crop database"),
        ("0", "Back"),
    ]
    while True:
        print_menu("Manage Crops", options)
        choice = validators.get_menu_choice("Enter your choice: ", ["1", "2", "3", "4", "5", "0"])
        if choice == "1":
            if farm.crops:
                show_farm_crops(farm, crops)
            else:
                display.print_warning("Your farm has no crops yet.")
        elif choice == "2":
            add_crop(farm, crops)
        elif choice == "3":
            edit_crop(farm, crops)
        elif choice == "4":
            delete_crop(farm, crops)
        elif choice == "5":
            search_crops(crops)
        else:
            return


# ---------- Weather and Schedule ----------

def fetch_weather_for_farm(farm):
    """Return the weather for the farm's city, or None if it cannot be obtained."""
    display.print_info(f"Fetching weather for {farm.city}...")
    try:
        weather, from_cache = get_weather(farm.city)
    except WeatherError as error:
        display.print_error(str(error))
        return None
    if from_cache:
        display.print_warning(f"No internet connection. Showing data saved on {weather['fetched_at']}.")
    return weather


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


# ---------- Log Irrigation and Savings Report ----------

def log_irrigation(farm, crops):
    if farm is None:
        display.print_warning("Create your farm first (option 1).")
        return
    crop_id = choose_farm_crop(farm, crops, "log")
    if crop_id is None:
        return
    volume_m3 = validators.get_positive_number("Water used (m3): ")
    date = validators.get_date("Date (YYYY-MM-DD, press Enter for today): ")
    try:
        farm.add_irrigation_log(crop_id, date, volume_m3)
    except ValueError as error:
        display.print_error(str(error))
        return
    save_farm(farm)
    display.print_success(f"Logged {volume_m3} m3 for {get_crop_name(crops, crop_id)} on {date}.")


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


# ---------- Main loop ----------

def main():
    crops = load_crops()
    farm = load_farm()
    valid_choices = [number for number, _ in MAIN_MENU]

    while True:
        print_menu("Smart Irrigation Planner", MAIN_MENU)
        choice = validators.get_menu_choice("Enter your choice: ", valid_choices)
        if choice == "1":
            farm = manage_farm(farm)
        elif choice == "2":
            manage_crops(farm, crops)
        elif choice == "3":
            view_weather(farm, crops)
        elif choice == "4":
            show_irrigation_schedule(farm, crops)
        elif choice == "5":
            log_irrigation(farm, crops)
        elif choice == "6":
            show_savings_report(farm, crops)
        elif choice in COMING_SOON:
            display.print_info("This feature is coming soon.")
        else:
            display.print_success("Goodbye!")
            break


if __name__ == "__main__":
    main()