from menus.roles import Farmer, Manager
from utils import display
from utils.file_handler import load_crops, load_farm
from utils.menu import Menu


class SmartIrrigationApp:
    """This is the main class"""

    def __init__(self):
        self._crops = load_crops()
        self._farm = load_farm()
        self._users = [Farmer(self), Manager(self)]

    @property
    def crops(self):
        return self._crops

    @property
    def farm(self):
        return self._farm

    @farm.setter
    def farm(self, new_farm):
        self._farm = new_farm

    def _build_menu(self):
        # Collect the actions of every user and number them.
        options = []
        handlers = {}
        for user in self._users:  
            for label, handler in user.get_actions():
                key = str(len(options) + 1)
                options.append((key, label))
                handlers[key] = handler
        exit_key = str(len(options) + 1)
        options.append((exit_key, "Exit"))
        return options, handlers, exit_key

    def run(self):
        options, handlers, exit_key = self._build_menu()
        menu = Menu("Smart Irrigation Planner", options)
        while True:
            choice = menu.choose()
            if choice == exit_key:
                display.print_success("Goodbye!")
                break
            handlers[choice]()


if __name__ == "__main__":
    try:
        SmartIrrigationApp().run()
    except KeyboardInterrupt:
        print("\nGoodbye..")