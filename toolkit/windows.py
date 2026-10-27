# Python Modules and Packages
import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys

from .helpers import ToolError


# Python Functions, Arguments and Return Values
def system_program(name):
    return str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / name)


def run_command(arguments, utf8=False):
    # Exception Handling in Python
    try:
        # Python Flow Control - Conditionals
        result = subprocess.run(arguments, capture_output=True, text=True,
                                encoding="utf-8" if utf8 else "oem", errors="replace",
                                timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.TimeoutExpired as error:
        raise ToolError("Windows timed out. Check the current setting before retrying or restoring.") from error
    if result.returncode != 0:
        # Python String Operations
        message = result.stderr.strip() or result.stdout.strip() or "Windows command failed."
        raise ToolError(message)
    return result.stdout.strip()


def powershell(script, data=None):
    payload = base64.b64encode(json.dumps(data).encode("utf-8")).decode("ascii")
    prefix = (
        "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue'; "
        "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
        f"$data = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{payload}')) | ConvertFrom-Json; "
    )
    encoded = base64.b64encode((prefix + script).encode("utf-16-le")).decode("ascii")
    executable = system_program(r"WindowsPowerShell\v1.0\powershell.exe")
    # Python Data Structures - List
    return run_command([executable, "-NoLogo", "-NoProfile", "-NonInteractive",
                        "-EncodedCommand", encoded], utf8=True)


def powershell_json(script, data=None):
    output = powershell(script, data)
    try:
        return json.loads(output) if output else None
    except json.JSONDecodeError as error:
        raise ToolError("Windows returned unexpected data; no further action was taken.") from error


def is_admin():
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def require_admin():
    if not is_admin():
        raise ToolError("Windows does not permit this setting change with the current account.")


def request_admin(action, settings_folder):
    if action not in {"dns-change", "dns-automatic", "dns-restore", "dns-cache"}:
        raise ValueError("Unknown administrator action.")
    entry_point = Path(__file__).resolve().parents[1] / "main.py"
    if not entry_point.is_file():
        raise ToolError("The application entry point could not be found.")
    settings_folder = Path(settings_folder).resolve(strict=True)
    parameters = subprocess.list2cmdline([
        "-B", str(entry_point), "--admin-action", action,
        "--settings-dir", str(settings_folder),
    ])
    import pythoncom
    import pywintypes
    import win32api
    import win32con
    from win32com.shell import shell, shellcon

    pythoncom.CoInitialize()
    try:
        process = shell.ShellExecuteEx(
            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
            lpVerb="runas",
            lpFile=sys.executable,
            lpParameters=parameters,
            lpDirectory=str(entry_point.parent),
            nShow=win32con.SW_SHOWNORMAL,
        )
        handle = process.get("hProcess")
        if handle:
            win32api.CloseHandle(handle)
        return True
    except pywintypes.error as error:
        if error.winerror == 1223:
            return False
        raise ToolError(f"Windows could not open the administrator window: {error}") from error
    finally:
        pythoncom.CoUninitialize()


def is_critical_process(pid):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    # Python Data Structures - Tuple
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.IsProcessCritical.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL))
    kernel.IsProcessCritical.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return True
    try:
        critical = wintypes.BOOL()
        if not kernel.IsProcessCritical(handle, ctypes.byref(critical)):
            return True
        return bool(critical.value)
    finally:
        kernel.CloseHandle(handle)


def is_fixed_drive(path):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetDriveTypeW.argtypes = (wintypes.LPCWSTR,)
    kernel.GetDriveTypeW.restype = wintypes.UINT
    return kernel.GetDriveTypeW(str(path.anchor)) == 3
