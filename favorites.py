import json
from pathlib import Path


FAVORITES_FILE = Path(__file__).resolve().parent / "favorites.json"


def load_favorites():
    if not FAVORITES_FILE.exists():
        return []

    try:
        with FAVORITES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_favorites(favorites):
    try:
        with FAVORITES_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                favorites,
                file,
                indent=4,
                ensure_ascii=False,
            )
    except OSError:
        print("❌ Could not save favorites.")


def add_favorite(country_name):
    favorites = load_favorites()

    if country_name not in favorites:
        favorites.append(country_name)
        save_favorites(favorites)
        return True

    return False


def remove_favorite(country_name):
    favorites = load_favorites()

    if country_name in favorites:
        favorites.remove(country_name)
        save_favorites(favorites)
        return True

    return False


def is_favorite(country_name):
    return country_name in load_favorites()


def show_favorites(return_data=False):
    favorites = load_favorites()

    if return_data:
        return favorites

    if not favorites:
        print("\nNo favorite countries yet.")
        return favorites

    print("\n⭐ Favorite Countries:\n")

    for index, country_name in enumerate(favorites, start=1):
        print(f"{index}. {country_name}")

    return favorites