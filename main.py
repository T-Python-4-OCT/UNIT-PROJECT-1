from menus.farm_menu import manage_crops, manage_farm
from menus.manager_menu import manager_panel
from menus.report_menu import log_irrigation, show_savings_report
from menus.weather_menu import show_irrigation_schedule, view_weather
from utils import display, validators
from utils.file_handler import load_crops, load_farm
from utils.ui_helpers import print_menu

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
        elif choice == "7":
            manager_panel(farm, crops)
        else:
            display.print_success("Goodbye..")
            break


if __name__ == "__main__":
    main()