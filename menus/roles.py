from abc import ABC, abstractmethod

from menus import farm_menu, manager_menu, report_menu, weather_menu


class User(ABC):
    """Base class for the people who use the program (abstract: it cannot be created directly)."""

    role_name = "User"

    def __init__(self, app):
        self._app = app  # the running application, which owns the farm and the crops

    @abstractmethod
    def get_actions(self):
        """Return a list of (label, function) pairs that this kind of user can run."""

    def __str__(self):
        return self.role_name


class Farmer(User):
    """The farmer registers a farm, plans irrigation, and tracks water use."""

    role_name = "Farmer"

    def get_actions(self):
        return [
            ("Manage Farm", self.manage_farm),
            ("Manage Crops", self.manage_crops),
            ("View Weather", self.view_weather),
            ("Get Irrigation Schedule", self.show_schedule),
            ("Log Irrigation", self.log_irrigation),
            ("View Savings Report", self.show_savings_report),
        ]

    def manage_farm(self):
        self._app.farm = farm_menu.manage_farm(self._app.farm)

    def manage_crops(self):
        farm_menu.manage_crops(self._app.farm, self._app.crops)

    def view_weather(self):
        weather_menu.view_weather(self._app.farm, self._app.crops)

    def show_schedule(self):
        weather_menu.show_irrigation_schedule(self._app.farm, self._app.crops)

    def log_irrigation(self):
        report_menu.log_irrigation(self._app.farm, self._app.crops)

    def show_savings_report(self):
        report_menu.show_savings_report(self._app.farm, self._app.crops)


class Manager(User):
    """The manager controls the crop database, the statistics, and the water price."""

    role_name = "Manager"

    def get_actions(self):
        return [("Manager Panel", self.open_panel)]

    def open_panel(self):
        manager_menu.manager_panel(self._app.farm, self._app.crops)