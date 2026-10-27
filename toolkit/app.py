# Python Modules and Packages
from .battery import BatteryTool
from .cleanup import CleanupTool
from .hardware import HardwareTool
from .helpers import run_menu
from .memory import MemoryTool
from .network import NetworkTool
from .storage import SettingsStore
from .terminal import console_text, new_badge


# Python OOP - Classes
class ToolkitApp:
    def __init__(self, settings_folder=None):
        self.store = SettingsStore(settings_folder)
        self.cleanup = CleanupTool(self.store)
        self.network = NetworkTool(self.store)
        self.battery = BatteryTool(self.store)
        self.memory = MemoryTool(self.store)
        self.hardware = HardwareTool()

    def run(self, admin_action=None):
        print("System Toolkit for Windows 10/11")
        print(f"Restoration data and activity log: {self.store.folder}")
        print("Use one Toolkit window at a time so saved settings stay consistent.")
        if self.store.data["backups"]:
            print("Saved restoration data exists. Network and battery menus can restore it.")
        # Python Data Structures - Dictionary
        actions = {
            "1": ("Clean up files", self.cleanup.run),
            "2": ("Network optimization", self.network.run),
            "3": ("Laptop battery optimization", self.battery.run),
            "4": ("RAM cleanup", self.memory.run),
            "5": (f"{console_text('PC Parts & Health', 'PC Parts & Health')} {new_badge()}", self.hardware.run),
        }
        admin_actions = {
            "dns-change": self.network.change_dns,
            "dns-automatic": self.network.automatic_dns,
            "dns-restore": self.network.restore_dns,
            "dns-cache": self.network.refresh_dns_cache,
        }
        run_menu("SYSTEM TOOLKIT", actions, back_key="6", back_label="Exit",
                 initial_action=admin_actions.get(admin_action))
        print("Goodbye.")
