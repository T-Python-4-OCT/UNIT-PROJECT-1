# Python Modules and Packages
import csv
import http.client
import io
import json
import math
import os
from pathlib import Path
import re

from .helpers import ToolError
from .windows import run_command, system_program


# Python Functions, Arguments and Return Values
def temperature_celsius(value):
    if value is None or isinstance(value, bool):
        return None
    fahrenheit = False
    if isinstance(value, str):
        match = re.fullmatch(r"\s*(-?\d+(?:[.,]\d+)?)\s*(?:°?\s*([CF]))?\s*", value, re.IGNORECASE)
        if not match:
            return None
        value = match[1].replace(",", ".")
        fahrenheit = (match[2] or "").upper() == "F"
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if fahrenheit:
        value = (value - 32) * 5 / 9
    return value if math.isfinite(value) and -100 <= value <= 200 else None


def nvidia_temperatures():
    try:
        import pynvml
    except ImportError:
        return None
    result = {"hardware": [], "sensors": []}
    initialized = False
    try:
        pynvml.nvmlInit()
        initialized = True
        for index in range(min(pynvml.nvmlDeviceGetCount(), 64)):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(index)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8", errors="replace")
                value = temperature_celsius(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
                identifier = f"nvidia/{index}"
                result["hardware"].append({"Name": name, "Identifier": identifier, "HardwareType": "GpuNvidia"})
                if value is not None:
                    result["sensors"].append({"Parent": identifier, "SensorType": "Temperature", "Value": value})
            except pynvml.NVMLError:
                continue
    except (pynvml.NVMLError, OSError):
        return None
    finally:
        if initialized:
            try:
                pynvml.nvmlShutdown()
            except pynvml.NVMLError:
                pass
    return result if result["sensors"] else None


def nvidia_command_temperatures():
    candidates = [Path(system_program("nvidia-smi.exe"))]
    program_files = os.environ.get("ProgramW6432") or os.environ.get("ProgramFiles")
    if program_files:
        candidates.append(Path(program_files) / "NVIDIA Corporation" / "NVSMI" / "nvidia-smi.exe")
    for executable in candidates:
        if not executable.is_file():
            continue
        try:
            output = run_command([str(executable), "--query-gpu=name,temperature.gpu", "--format=csv,noheader,nounits"])
        except (ToolError, OSError):
            continue
        result = {"hardware": [], "sensors": []}
        for index, row in enumerate(csv.reader(io.StringIO(output))):
            if len(row) != 2:
                continue
            identifier = f"nvidia/{index}"
            result["hardware"].append({"Name": row[0].strip(), "Identifier": identifier, "HardwareType": "GpuNvidia"})
            value = temperature_celsius(row[1])
            if value is not None:
                result["sensors"].append({"Parent": identifier, "SensorType": "Temperature", "Value": value})
        if result["sensors"]:
            return result
    return None


def libre_sensor_tree(tree):
    result = {"hardware": [], "sensors": []}
    pending = [(tree, None)]
    visited = 0
    while pending and visited < 4096:
        node, parent = pending.pop()
        visited += 1
        if not isinstance(node, dict):
            continue
        identifier = node.get("HardwareId")
        if isinstance(identifier, str):
            if re.fullmatch(r"/[a-z0-9]*cpu/\d+", identifier):
                kind = "Cpu"
            else:
                kind = {"gpu-nvidia": "GpuNvidia", "gpu-amd": "GpuAmd", "gpu-ati": "GpuAti",
                        "gpu-intel": "GpuIntel"}.get(identifier.strip("/").split("/")[0])
            parent = identifier if kind else None
            if kind:
                result["hardware"].append({"Name": node.get("Text"), "Identifier": identifier, "HardwareType": kind})
        sensor_id = node.get("SensorId")
        if (parent and node.get("Type") == "Temperature" and isinstance(sensor_id, str)
                and sensor_id.startswith(parent + "/temperature/")):
            value = temperature_celsius(node.get("RawValue"))
            if value is None:
                value = temperature_celsius(node.get("Value"))
            if value is not None:
                result["sensors"].append({"Parent": parent, "SensorType": "Temperature", "Value": value})
        children = node.get("Children", [])
        if isinstance(children, list):
            pending.extend((child, parent) for child in children[:4096 - visited])
    return result if result["sensors"] else None


def libre_temperatures():
    connection = http.client.HTTPConnection("127.0.0.1", 8085, timeout=1)
    try:
        connection.request("GET", "/data.json", headers={"Accept": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            return None
        content = response.read(2 * 1024 * 1024 + 1)
        if len(content) > 2 * 1024 * 1024:
            return None
        return libre_sensor_tree(json.loads(content.decode("utf-8-sig")))
    except (OSError, http.client.HTTPException, ValueError, UnicodeError, RecursionError):
        return None
    finally:
        connection.close()


def read_temperature_sources():
    nvidia = nvidia_temperatures() or nvidia_command_temperatures()
    libre = libre_temperatures()
    return [source for source in (nvidia, libre) if source is not None]
