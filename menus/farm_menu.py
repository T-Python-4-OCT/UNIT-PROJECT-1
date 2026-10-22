from models.farm import Farm
from utils import display, validators
from utils.file_handler import save_farm
from utils.ui_helpers import (
    choose_farm_crop,
    choose_irrigation_type,
    get_crop_name,
    print_menu,
    show_database_crops,
    show_farm_crops,
)


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