import json
from pathlib import Path
from models.crop import Crop
from models.farm import Farm

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CROPS_FILE = DATA_DIR / "crops.json"
FARM_FILE = DATA_DIR / "farms.json"


def load_json(file_path, default):
    """Read a JSON file. Return `default` if it is missing or corrupted."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"[WARNING] {file_path.name} is corrupted. Using default data.")
        return default


def save_json(file_path, data):
    """Write data to a JSON file, creating the folder if needed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def load_crops():
    """Return a dictionary {crop_id: Crop} from crops.json."""
    raw_crops = load_json(CROPS_FILE, {})
    crops = {}
    for crop_id, data in raw_crops.items():
        try:
            crops[crop_id] = Crop.from_dict(crop_id, data)
        except KeyError as error:
            print(f"[WARNING] Skipping crop '{crop_id}': missing field {error}.")
    return crops


def save_crops(crops):
    """Save a dictionary {crop_id: Crop} to crops.json."""
    save_json(CROPS_FILE, {crop_id: crop.to_dict() for crop_id, crop in crops.items()})


def load_farm():
    """Return the saved Farm, or None if no farm has been registered yet."""
    data = load_json(FARM_FILE, {})
    if not data:
        return None
    try:
        return Farm.from_dict(data)
    except KeyError as error:
        print(f"[WARNING] Farm data is incomplete: missing field {error}.")
        return None


def save_farm(farm):
    save_json(FARM_FILE, farm.to_dict())