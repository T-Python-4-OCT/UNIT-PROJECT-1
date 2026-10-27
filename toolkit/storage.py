# Python Modules and Packages
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone


# Python OOP - Classes
class SettingsStore:
    # Python Functions, Arguments and Return Values
    def __init__(self, folder=None):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        # Python Flow Control - Conditionals
        self.folder = Path(folder) if folder is not None else base / "SystemToolkit"
        self.folder.mkdir(parents=True, exist_ok=True)
        self.path = self.folder / "settings.json"
        # Python Data Structures - Dictionary
        self.data = {"version": 1, "backups": {}}
        if self.path.exists():
            # Python File I/O
            with self.path.open("r", encoding="utf-8") as file:
                self.data = json.load(file)
            if (not isinstance(self.data, dict) or self.data.get("version") != 1
                    or not isinstance(self.data.get("backups"), dict)):
                # Python String Operations
                raise ValueError(f"Invalid restoration file; preserve it for recovery: {self.path}")

    def get(self, key):
        return self.data["backups"].get(key)

    def save(self, updated):
        temporary = None
        # Exception Handling in Python
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.folder,
                                             prefix="settings-", suffix=".tmp", delete=False) as file:
                temporary = Path(file.name)
                json.dump(updated, file, indent=2)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.path)
            self.data = updated
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def remember(self, key, value):
        if key not in self.data["backups"]:
            backups = dict(self.data["backups"])
            backups[key] = value
            self.save({"version": 1, "backups": backups})

    def forget(self, key):
        backups = dict(self.data["backups"])
        backups.pop(key, None)
        self.save({"version": 1, "backups": backups})

    def log(self, action, outcome):
        try:
            stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            with (self.folder / "actions.log").open("a", encoding="utf-8") as file:
                file.write(f"{stamp} {action}: {outcome}\n")
        except OSError as error:
            print(f"Could not write the activity log: {error}")
