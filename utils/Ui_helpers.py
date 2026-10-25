from models.farm import IRRIGATION_TYPES
from services.weather import WeatherError, get_weather
from utils import display
from utils.menu import Menu


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


def select_from_list(title, labels, allow_back=True):
    """Let the user pick one item with the arrow keys.

    Return its index (starting at 0), or None if the user chose Back.
    """
    options = [(str(number), label) for number, label in enumerate(labels, start=1)]
    back_key = str(len(labels) + 1)  # Back is the last number in the list
    if allow_back:
        options.append((back_key, "Back"))
    key = Menu(title, options).choose()
    return None if key == back_key else int(key) - 1


def choose_irrigation_type():
    labels = [irrigation_type.capitalize() for irrigation_type in IRRIGATION_TYPES]
    index = select_from_list("Choose irrigation type", labels, allow_back=False)
    return IRRIGATION_TYPES[index]


def choose_farm_crop(farm, crops, action):
    """Let the user pick one of the crops already on the farm. Return its id or None."""
    if not farm.crops:
        display.print_warning("Your farm has no crops yet.")
        return None
    show_farm_crops(farm, crops)
    names = [get_crop_name(crops, item["crop_id"]) for item in farm.crops]
    index = select_from_list(f"Select the crop to {action}", names)
    if index is None:
        return None
    return farm.crops[index]["crop_id"]


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