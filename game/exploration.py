# التنقل بين المواقع وشروط فتحها
# Exploration system with Fantasy Forest Rich styling.

import json
from pathlib import Path

from rich.panel import Panel
from rich.text import Text

from ui.effects import console


LOCATIONS_FILE = Path(__file__).parent / "data" / "locations.json"
LOCATIONS_AR_FILE = Path(__file__).parent / "data" / "locations_ar.json"

FOREST_GREEN = "#2F5249"
ANTIQUE_GOLD = "#C5A46D"
SOFT_GREEN = "#A3B18A"
LOCKED_GRAY = "#858585"


def load_locations():
    with LOCATIONS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data["regions"]


class Exploration:
    def __init__(self):
        self.regions = load_locations()

        with LOCATIONS_AR_FILE.open("r", encoding="utf-8") as file:
            arabic_regions = json.load(file)["regions"]

        self.arabic_texts = {}

        for region in arabic_regions:
            original_region = next(
                item for item in self.regions
                if item["id"] == region["id"]
            )

            self.arabic_texts[original_region["name"]] = region["name"]
            self.arabic_texts[original_region["description"]] = (
                region["description"]
            )

            for location in region["locations"]:
                original_location = next(
                    item for item in original_region["locations"]
                    if item["id"] == location["id"]
                )

                self.arabic_texts[original_location["name"]] = (
                    location["name"]
                )
                self.arabic_texts[original_location["description"]] = (
                    location["description"]
                )

        self.current_region = 0
        self.visited_locations = set()
        self.completed_locations = set()

    def get_current_region(self):
        return self.regions[self.current_region]

    def get_locations(self):
        return self.get_current_region()["locations"]

    def is_unlocked(self, location):
        requirements = location.get("requires", [])

        return all(
            required in self.completed_locations
            for required in requirements
        )

    def translate_location(self, text, loc):
        if loc.language == "ar":
            text = self.arabic_texts.get(text, text)

        return loc.format_arabic(text)

    def show_locations(self, loc):
        region = self.get_current_region()

        region_name = self.translate_location(region["name"], loc)
        region_description = self.translate_location(
            region["description"], loc
        )

        console.print()

        console.print(
            Panel(
                Text(region_description, style=SOFT_GREEN),
                title=f"🌳 {region_name}",
                title_align="center",
                border_style=FOREST_GREEN,
                padding=(1, 2),
                expand=False,
            )
        )

        console.print(
            Text(
                f"\n🧭 {loc.display_text('available_locations')}:",
                style=ANTIQUE_GOLD,
            )
        )

        for index, location in enumerate(self.get_locations(), start=1):
            if location["id"] in self.completed_locations:
                icon = "✅"
                status_color = ANTIQUE_GOLD
                status = loc.display_text("completed")

            elif self.is_unlocked(location):
                icon = "🔓"
                status_color = SOFT_GREEN
                status = loc.display_text("available")

            else:
                icon = "🔒"
                status_color = LOCKED_GRAY
                status = loc.display_text("locked")

            name = self.translate_location(location["name"], loc)

            line = Text()
            line.append(f"{index}. {icon} ")
            line.append(name, style=status_color)
            line.append(f" [{status}]", style=LOCKED_GRAY)

            console.print(line)

    def visit_location(self, location_number, loc):
        locations = self.get_locations()

        if not 1 <= location_number <= len(locations):
            console.print(
                Text(
                    loc.display_text("invalid_option"),
                    style="red",
                )
            )
            return None

        location = locations[location_number - 1]

        if not self.is_unlocked(location):
            message = (
                "هذا الموقع لا يزال مغلقًا."
                if loc.language == "ar"
                else "This location is locked."
            )

            console.print(
                Text(loc.format_arabic(message), style="red")
            )
            return None

        self.visited_locations.add(location["id"])

        name = self.translate_location(location["name"], loc)
        description = self.translate_location(
            location["description"], loc
        )

        console.print()
        console.print(
            Panel(
                Text(description, style=SOFT_GREEN),
                title=f"✨ {name}",
                border_style=ANTIQUE_GOLD,
                padding=(1, 2),
                expand=False,
            )
        )

        return location

    def move_to_next_region(self, loc):
        region = self.get_current_region()

        required_locations = [
            location["id"]
            for location in region["locations"]
            if not location.get("optional", False)
        ]

        if not all(
            location_id in self.completed_locations
            for location_id in required_locations
        ):
            message = (
                "أكمل المواقع الرئيسية قبل مغادرة المنطقة."
                if loc.language == "ar"
                else "Complete all main locations before leaving this region."
            )

            console.print(
                Text(loc.format_arabic(message), style="red")
            )
            return False

        if self.current_region + 1 >= len(self.regions):
            message = (
                "لقد وصلت إلى المنطقة الأخيرة."
                if loc.language == "ar"
                else "You have reached the final region."
            )

            console.print(
                Text(loc.format_arabic(message), style=ANTIQUE_GOLD)
            )
            return False

        self.current_region += 1

        name = self.translate_location(
            self.get_current_region()["name"], loc
        )

        console.print(
            Panel(
                Text(f"🌲 {name}", style=ANTIQUE_GOLD),
                border_style=FOREST_GREEN,
                expand=False,
            )
        )

        return True

    def complete_location(self, location_id):
        self.visited_locations.add(location_id)
        self.completed_locations.add(location_id)