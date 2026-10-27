# Python Modules and Packages
import re
from uuid import UUID

import psutil

from .helpers import ToolError, confirm, logged_action, run_menu
from .windows import run_command, system_program


GUID_PATTERN = r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}"
POWER_SAVER_GUID = "a1841308-3541-4fab-bc81-f71556f20b4a"


# Python OOP - Classes
class BatteryTool:
    # Python Functions, Arguments and Return Values
    def __init__(self, store):
        self.store = store

    def run(self):
        # Python Data Structures - Dictionary
        # Python Data Structures - Tuple
        run_menu("LAPTOP BATTERY OPTIMIZATION", {
            "1": ("Show battery status and active power plan", self.status),
            "2": ("Use the installed Power Saver plan", self.use_power_saver),
            "3": ("Restore the saved power plan", self.restore),
        })

    def powercfg(self, *arguments):
        # Python Data Structures - List
        return run_command([system_program("powercfg.exe"), *arguments])

    def active_plan(self):
        output = self.powercfg("/getactivescheme")
        match = re.search(GUID_PATTERN, output)
        # Python Flow Control - Conditionals
        if not match:
            raise ToolError("Windows did not report an active power-plan GUID.")
        # Python String Operations
        return match.group().lower()

    def available_plans(self):
        output = self.powercfg("/list")
        # Python Data Structures - Set
        return {guid.lower() for guid in re.findall(GUID_PATTERN, output)}

    def battery_status(self):
        # Exception Handling in Python
        try:
            battery = psutil.sensors_battery()
        except (AttributeError, NotImplementedError):
            print("Battery monitoring is unsupported on this computer.")
            return
        if battery is None:
            print("No battery was detected, or its information is unavailable.")
            return
        print(f"Battery: {battery.percent:.0f}%")
        charging = "Plugged in (charging, full, or charging paused)" if battery.power_plugged else "Running on battery"
        print(f"Power status: {charging}")

    def status(self):
        self.battery_status()
        print(f"Active power plan: {self.active_plan()}")

    def set_and_verify(self, guid):
        
        guid = str(UUID(str(guid)))
        if guid not in self.available_plans():
            raise ToolError("That power plan is no longer installed. The restoration backup is kept.")
        try:
            self.powercfg("/setactive", guid)
        except ToolError as error:
            raise ToolError(f"Windows refused the power-plan change: {error}\n"
                            "Device policy may prevent it; administrator access may be required.") from error
        if self.active_plan() != guid:
            raise ToolError("Windows did not confirm the requested plan. The restoration backup is kept.")

    # Python Decorators
    @logged_action
    def use_power_saver(self):
        self.battery_status()
        if POWER_SAVER_GUID not in self.available_plans():
            print("The standard Power Saver plan is unavailable on this device.")
            print("Some Modern Standby computers expose only Balanced. Check Windows Settings > System > Power & battery.")
            return "unsupported power plan"
        active = self.active_plan()
        if active == POWER_SAVER_GUID:
            print("The Power Saver plan is already active.")
            return "already Power Saver"
        print("Power Saver can reduce energy use by reducing performance and changing device power behavior.")
        print("It becomes the active plan for both AC and battery use. Work may run more slowly.")
        print("Some PCs require administrator access or block changes through device policy.")
        if not confirm("Save the current plan and activate Power Saver?"):
            return "cancelled"
        self.store.remember("power", {"guid": active})
        self.set_and_verify(POWER_SAVER_GUID)
        print("Power Saver is active and verified. Use 'Restore the saved power plan' to undo it.")
        return "Power Saver verified"

    @logged_action
    def restore(self):
        backup = self.store.get("power")
        if backup is None:
            print("There is no saved power plan to restore.")
            return "no backup"
        if not isinstance(backup, dict) or not backup.get("guid"):
            raise ValueError("Invalid power restoration data; preserve settings.json for inspection.")
        guid = str(UUID(str(backup["guid"])))
        if not confirm(f"Restore the original power plan ({guid})?"):
            return "cancelled"
        self.set_and_verify(guid)
        self.store.forget("power")
        print("Original power plan restored and verified.")
        return "power plan restored and verified"
