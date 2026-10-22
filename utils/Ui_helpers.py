from models.farm import IRRIGATION_TYPES
from services.weather import WeatherError, get_weather
from utils import display, validators


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
        [index, crop.name, crop.kc, crop.min_temp]
        for index, crop in enumerate(crop_list, start=1)
    ]
    display.print_table(rows, ["#", "Crop", "Kc", "Min Temp (C)"])


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