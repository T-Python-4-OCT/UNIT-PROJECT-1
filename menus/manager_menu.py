from models.crop import Crop, make_crop_id
from services.reports import get_logged_usage, get_planted_ranking
from utils import display, validators
from utils.file_handler import load_settings, save_crops, save_settings
from utils.ui_helpers import print_menu, show_database_crops


def choose_database_crop(crops, action):
    """Let the Manager pick any crop type from the database. Return it or None."""
    if not crops:
        display.print_warning("The crop database is empty.")
        return None
    crop_list = list(crops.values())
    show_database_crops(crop_list)
    index = validators.get_number_in_range(f"Enter the number of the crop to {action}: ", 1, len(crop_list))
    return crop_list[index - 1]


def add_crop_type(crops):
    name = validators.get_text("Crop name (English letters): ")
    crop_id = make_crop_id(name)
    if not crop_id:
        display.print_error("The name must contain English letters or numbers.")
        return
    if crop_id in crops:
        display.print_error(f"'{name}' already exists in the database.")
        return
    kc = validators.get_number("Crop coefficient Kc (0.1 to 2): ", 0.1, 2)
    min_temp = validators.get_number("Minimum safe temperature in C (-30 to 40): ", -30, 40)
    crops[crop_id] = Crop(crop_id, name, kc, min_temp)
    save_crops(crops)
    display.print_success(f"{name} added to the database.")


def edit_crop_type(crops):
    crop = choose_database_crop(crops, "edit")
    if crop is None:
        return
    name = validators.get_text(f"New name (Enter to keep '{crop.name}'): ", allow_blank=True)
    kc = validators.get_number(f"New Kc (Enter to keep {crop.kc}): ", 0.1, 2, allow_blank=True)
    min_temp = validators.get_number(
        f"New minimum temperature (Enter to keep {crop.min_temp}): ", -30, 40, allow_blank=True
    )
    if name is None and kc is None and min_temp is None:
        display.print_info("Nothing was changed.")
        return
    if name is not None:
        crop.name = name
    if kc is not None:
        crop.kc = kc
    if min_temp is not None:
        crop.min_temp = min_temp
    save_crops(crops)
    display.print_success(f"{crop.name} updated.")


def delete_crop_type(farm, crops):
    crop = choose_database_crop(crops, "delete")
    if crop is None:
        return
    if farm is not None and farm.find_crop(crop.crop_id):
        display.print_error(f"Cannot delete {crop.name}: it is planted on the farm. Remove it from the farm first.")
        return
    if not validators.confirm(f"Delete {crop.name} from the database?"):
        display.print_info("Deletion cancelled.")
        return
    del crops[crop.crop_id]
    save_crops(crops)
    display.print_success(f"{crop.name} deleted from the database.")


def show_statistics(farm, crops):
    display.print_title("Statistics")
    print(f"Crop types in the database: {len(crops)}")
    if farm is None:
        display.print_warning("No farm registered yet, so there is no farm data to analyse.")
        return

    print(f"Farm: {farm.farm_name} ({farm.city})")
    if farm.crops:
        ranking = get_planted_ranking(farm, crops)
        rows = [
            [rank, item["crop_name"], item["area_m2"], f"{round(item['share_percent'])}%"]
            for rank, item in enumerate(ranking, start=1)
        ]
        print("\nMost planted crops (by area):")
        display.print_table(rows, ["Rank", "Crop", "Area (m2)", "Share"])
    else:
        display.print_warning("The farm has no crops yet.")

    water_price = load_settings()["water_price_per_m3"]
    logged = get_logged_usage(farm, crops, water_price)
    total_used = sum(item["volume_m3"] for item in logged)
    print(f"Total irrigation logged: {round(total_used, 1)} m3 ({round(total_used * water_price, 2)} SAR)")
    print(f"Log entries: {len(farm.irrigation_log)}")

    if farm.last_savings:
        saving = farm.last_savings
        print(f"Latest estimated weekly saving: {saving['saved_m3']} m3 ({saving['saved_percent']}%) "
              f"on {saving['date']}")
    else:
        display.print_info("No savings report yet. Run option 6 to estimate the saving.")


def change_water_price():
    settings = load_settings()
    print(f"Current water price: {settings['water_price_per_m3']} SAR per m3")
    settings["water_price_per_m3"] = validators.get_positive_number("New price in SAR per m3: ")
    save_settings(settings)
    display.print_success(f"Water price updated to {settings['water_price_per_m3']} SAR per m3.")


def manager_panel(farm, crops):
    options = [
        ("1", "View crop database"),
        ("2", "Add crop type"),
        ("3", "Edit crop type"),
        ("4", "Delete crop type"),
        ("5", "View statistics"),
        ("6", "Change water price"),
        ("0", "Back"),
    ]
    while True:
        print_menu("Manager Panel", options)
        choice = validators.get_menu_choice("Enter your choice: ", ["1", "2", "3", "4", "5", "6", "0"])
        if choice == "1":
            if crops:
                show_database_crops(list(crops.values()))
            else:
                display.print_warning("The crop database is empty.")
        elif choice == "2":
            add_crop_type(crops)
        elif choice == "3":
            edit_crop_type(crops)
        elif choice == "4":
            delete_crop_type(farm, crops)
        elif choice == "5":
            show_statistics(farm, crops)
        elif choice == "6":
            change_water_price()
        else:
            return