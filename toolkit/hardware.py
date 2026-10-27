# Python Modules and Packages
import math
import re

import psutil

from .helpers import ToolError, run_menu
from .terminal import console_text
from .temperatures import read_temperature_sources, temperature_celsius
from .windows import powershell_json


# Python String Operations
READ_HARDWARE = r"""
$unavailable = [Collections.Generic.List[string]]::new()
function Read-Parts($ClassName, $Properties, $Namespace = 'root/cimv2', [switch]$Optional) {
    try {
        @(Get-CimInstance -Namespace $Namespace -ClassName $ClassName -Property $Properties `
            -OperationTimeoutSec 2 -ErrorAction Stop | Select-Object -Property $Properties)
    } catch {
        if (-not $Optional) { $unavailable.Add($ClassName) }
    }
}
$cpu = @(Read-Parts 'Win32_Processor' @('Name'))
$memory = @(Read-Parts 'Win32_PhysicalMemory' @('Capacity', 'SMBIOSMemoryType', 'MemoryType'))
$gpu = @(Read-Parts 'Win32_VideoController' @('Name'))
$board = @(Read-Parts 'Win32_BaseBoard' @('Manufacturer', 'Product'))
$storage = @(Read-Parts 'MSFT_PhysicalDisk' @('FriendlyName', 'Size', 'HealthStatus') `
    'root/Microsoft/Windows/Storage' -Optional)
if ($storage.Count -eq 0) {
    $storage = @(Read-Parts 'Win32_DiskDrive' @('Model', 'Size') | ForEach-Object {
        [pscustomobject]@{ FriendlyName = $_.Model; Size = $_.Size; HealthStatus = $null }
    })
}
$temperatureSources = @(foreach ($namespace in @('root/LibreHardwareMonitor', 'root/OpenHardwareMonitor')) {
    $hardware = @(Read-Parts 'Hardware' @('Name', 'Identifier', 'HardwareType') $namespace -Optional)
    if ($hardware.Count -gt 0) {
        $sensors = @(Read-Parts 'Sensor' @('Name', 'Parent', 'SensorType', 'Value') $namespace -Optional |
            Where-Object { $_.SensorType -eq 'Temperature' })
        [pscustomobject]@{ hardware = $hardware; sensors = $sensors }
    }
})
[pscustomobject]@{
    cpu = $cpu; memory = $memory; gpu = $gpu; storage = $storage; board = $board
    temperature_sources = $temperatureSources; unavailable = @($unavailable.ToArray())
} | ConvertTo-Json -Depth 5 -Compress
"""


# Python Data Structures - Dictionary
SMBIOS_MEMORY_TYPES = {
    18: "DDR", 19: "DDR2", 20: "DDR2 FB-DIMM", 24: "DDR3", 26: "DDR4",
    27: "LPDDR", 28: "LPDDR2", 29: "LPDDR3", 30: "LPDDR4", 34: "DDR5", 35: "LPDDR5",
}
CIM_MEMORY_TYPES = {20: "DDR", 21: "DDR2", 22: "DDR2 FB-DIMM", 24: "DDR3", 26: "DDR4"}
DISK_HEALTH = {0: "Healthy", 1: "Warning", 2: "Unhealthy", 5: "Unknown"}
COMPONENT_NAMES = {
    "Win32_Processor": "CPU", "Win32_PhysicalMemory": "RAM type/capacity",
    "Win32_VideoController": "GPU", "Win32_BaseBoard": "board", "Win32_DiskDrive": "storage",
}


# Python Functions, Arguments and Return Values
def records(value):
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError, OverflowError):
        return None


def clean_name(value):
    if not isinstance(value, str):
        return "Unknown"
    text = " ".join("".join(char for char in value if char.isprintable() or char.isspace()).split())
    if text.casefold().strip(" .") in {
        "", "unknown", "none", "n/a", "not applicable", "not specified", "default string",
        "to be filled by o.e.m", "system product name",
    }:
        return "Unknown"
    return text.replace("(R)", "").replace("(TM)", "").strip()


def model_key(value):
    return re.sub(r"[^a-z0-9]", "", clean_name(value).casefold())


def capacity(value, binary=True):
    amount = number(value)
    if amount is None or amount <= 0:
        return "N/A"
    base = 1024 if binary else 1000
    unit = "GB" if amount < base ** 4 else "TB"
    amount /= base ** (3 if unit == "GB" else 4)
    return f"{amount:.1f}".removesuffix(".0") + f" {unit}"


def memory_summary(modules):
    if not modules:
        return "Unknown type | Installed: N/A"
    types = []
    sizes = []
    for module in modules:
        raw_type = number(module.get("SMBIOSMemoryType"))
        memory_type = SMBIOS_MEMORY_TYPES.get(raw_type)
        if memory_type is None and raw_type in (None, 0, 1, 2):
            memory_type = CIM_MEMORY_TYPES.get(number(module.get("MemoryType")))
        label = memory_type or "Unknown type"
        if label not in types:
            types.append(label)
        sizes.append(number(module.get("Capacity")))
    installed = sum(sizes) if all(size is not None and size > 0 for size in sizes) else None
    return f"{' + '.join(types)} | Installed: {capacity(installed)}"


def device_temperature(snapshot, name, kind, device_count):
    types = {"cpu"} if kind == "cpu" else {"gpunvidia", "gpuamd", "gpuati", "gpuintel"}
    if device_count > 1 and sum(
            model_key(item.get("Name")) == model_key(name) for item in records(snapshot.get(kind))) > 1:
        return None
    for source in records(snapshot.get("temperature_sources")):
        devices = [device for device in records(source.get("hardware"))
                   if str(device.get("HardwareType", "")).casefold() in types]
        matches = [device for device in devices
                   if clean_name(name) != "Unknown" and model_key(device.get("Name")) == model_key(name)]
        if not matches and kind == "cpu" and device_count == 1 and len(devices) == 1:
            matches = devices
        if len(matches) != 1:
            continue
        identifier = matches[0].get("Identifier")
        if not isinstance(identifier, str) or not identifier:
            continue
        values = [temperature_celsius(sensor.get("Value")) for sensor in records(source.get("sensors"))
                  if sensor.get("Parent") == identifier and sensor.get("SensorType") == "Temperature"]
        values = [value for value in values if value is not None]
        if values:
            return max(values)
    return None


# Python OOP - Classes
class HardwareTool:
    def run(self):
        run_menu(console_text("PC PARTS & HEALTH", "PC PARTS & HEALTH"), {
            "1": ("Refresh hardware details", self.show),
            "2": ("Temperature help", self.temperature_help),
        }, initial_action=self.show)

    def temperature_help(self):
        print("\nNVIDIA temperatures use the installed graphics driver automatically.")
        print("For CPU and other GPU sensors, open Libre Hardware Monitor:")
        print("1. Options > Remote Web Server > Interface / Port: 127.0.0.1, port 8085.")
        print("2. Options > Remote Web Server > Run. Keep it open, then refresh here.")
        print("Some sensors need Windows administrator approval in Libre Hardware Monitor.")
        print("Multiple sensors for one device show the highest current reading.")
        print("Unknown health means no health reading was available.")

    def show(self):
        print("\nReading PC parts...")
        try:
            snapshot = powershell_json(READ_HARDWARE)
            if not isinstance(snapshot, dict):
                raise ToolError("Windows returned no hardware details.")
        except (ToolError, OSError) as error:
            print(f"Hardware details unavailable: {error}")
            snapshot = {}
        sources = read_temperature_sources() + records(snapshot.get("temperature_sources"))
        snapshot["temperature_sources"] = sources
        for kind, types in (("cpu", {"cpu"}), ("gpu", {"gpunvidia", "gpuamd", "gpuati", "gpuintel"})):
            if not records(snapshot.get(kind)):
                for source in sources:
                    devices = [device for device in records(source.get("hardware"))
                               if str(device.get("HardwareType", "")).casefold() in types]
                    if devices:
                        snapshot[kind] = [{"Name": device.get("Name")} for device in devices]
                        break
        print(f"\n{console_text('🖥️ PC PARTS & HEALTH', 'PC PARTS & HEALTH')}\n")
        for kind, label in (("cpu", "CPU"), ("gpu", "GPU")):
            devices = records(snapshot.get(kind))
            for device in devices or [{}]:
                value = device_temperature(snapshot, device.get("Name"), kind, len(devices))
                temperature = f"{value:.0f}{console_text('°C', ' C')}" if value is not None else "N/A"
                print(f"{label + ':':<9}{clean_name(device.get('Name'))} | Temp: {temperature}")
            if kind == "cpu":
                summary = memory_summary(records(snapshot.get("memory")))
                try:
                    memory = psutil.virtual_memory()
                    used = max(0, memory.total - memory.available)
                    usage = f"{used / 1024 ** 3:.1f}/{memory.total / 1024 ** 3:.1f} GB used (usable)"
                except (OSError, psutil.Error, AttributeError, NotImplementedError):
                    usage = "Usage: N/A"
                print(f"{'RAM:':<9}{summary} | {usage}")
        disks = records(snapshot.get("storage"))
        for disk in disks or [{}]:
            health = DISK_HEALTH.get(number(disk.get("HealthStatus")), "Unknown")
            print(f"{'Storage:':<9}{clean_name(disk.get('FriendlyName'))} {capacity(disk.get('Size'), binary=False)}"
                  f" | Health: {health}")
        for board in records(snapshot.get("board")) or [{}]:
            parts = [clean_name(board.get(key)) for key in ("Manufacturer", "Product")]
            name = " ".join(dict.fromkeys(part for part in parts if part != "Unknown")) or "Unknown"
            print(f"{'Board:':<9}{name}")
        missing = [COMPONENT_NAMES[name] for name in snapshot.get("unavailable", []) if name in COMPONENT_NAMES]
        if missing:
            print(f"Windows could not read: {', '.join(missing)}.")
