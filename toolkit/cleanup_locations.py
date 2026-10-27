# Python Modules and Packages
import os
from pathlib import Path

from .helpers import ToolError
from .windows import powershell_json


READ_CLEANUP_LOCATIONS = r"""
$warnings = @()
$profiles = @()
$drives = @()
try {
    $profiles = @(Get-CimInstance Win32_UserProfile -Filter 'Special = FALSE' |
        Where-Object { $_.LocalPath } | Select-Object -ExpandProperty LocalPath)
} catch {
    $warnings += 'Windows could not list all local user profiles.'
}
try {
    $drives = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType = 3' |
        Select-Object -ExpandProperty DeviceID)
} catch {
    $warnings += 'Windows could not list all local fixed drives.'
}
[pscustomobject]@{ profiles = $profiles; drives = $drives; warnings = $warnings } |
    ConvertTo-Json -Depth 3 -Compress
"""


# Python Functions, Arguments and Return Values
def discover_cleanup_locations(user_temp):
    # Python Data Structures - List
    warnings = []
    # Exception Handling in Python
    # Python Data Structures - Tuple
    try:
        inventory = powershell_json(READ_CLEANUP_LOCATIONS)
        # Python Flow Control - Conditionals
        if (not isinstance(inventory, dict)
                or not all(isinstance(inventory.get(key), list) for key in ("profiles", "drives", "warnings"))):
            raise ToolError("Windows returned an unexpected cleanup-location list.")
        warnings.extend(inventory["warnings"])
    except (ToolError, OSError) as error:
        # Python Data Structures - Dictionary
        inventory = {"profiles": [], "drives": []}
        # Python String Operations
        warnings.append(f"Some locations could not be discovered: {error}")

    locations = []
    # Python Data Structures - Set
    seen = set()

    def add(path, label, days=1, suffixes=None):
        path = Path(path)
        if not path.is_absolute() or str(path).startswith("\\\\"):
            return
        path = Path(os.path.abspath(path))
        key = os.path.normcase(str(path))
        if key not in seen:
            seen.add(key)
            locations.append({"path": path, "label": label, "days": days, "suffixes": suffixes})

    def add_profile(local_data, label):
        add(local_data / "Temp", f"Temporary files - {label}")
        add(local_data / "CrashDumps", f"Old application crash dumps - {label}",
            days=7, suffixes={".dmp", ".mdmp"})
        add(local_data / "Microsoft" / "Windows" / "WER" / "ReportArchive",
            f"Archived error reports - {label}", days=7)

    user_temp = Path(user_temp)
    add_profile(user_temp.parent, "current user")
    # Python Flow Control - Loops
    for variable in ("TEMP", "TMP"):
        value = os.environ.get(variable)
        if value:
            path = Path(value)
            if path.name.casefold() in ("temp", "tmp") or path.parent.name.casefold() in ("temp", "tmp"):
                add(path, f"Temporary files - %{variable}%")

    for value in inventory["profiles"]:
        if isinstance(value, str) and value:
            profile = Path(value)
            add_profile(profile / "AppData" / "Local", profile.name)

    windows_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    program_data = Path(os.environ.get("ProgramData", r"C:\ProgramData"))
    add(windows_root / "Temp", "Windows temporary files")
    add(program_data / "Microsoft" / "Windows" / "WER" / "ReportArchive",
        "Archived Windows error reports", days=7)

    for drive in inventory["drives"]:
        if isinstance(drive, str) and len(drive) == 2 and drive[0].isascii() and drive[0].isalpha() and drive[1] == ":":
            for name in ("Temp", "Tmp"):
                add(Path(drive + "\\") / name, f"Temporary files - {drive}")

    return locations, warnings
