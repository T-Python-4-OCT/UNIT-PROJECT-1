# Python Modules and Packages
import os
from pathlib import Path

import psutil

from .helpers import ToolError, confirm, format_bytes, logged_action, read_number, run_menu
from .windows import is_critical_process, powershell_json


# Python Data Structures - Set
BLOCKED_NAMES = {
    "system", "registry", "secure system", "idle", "system idle process",
    "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe", "services.exe",
    "lsass.exe", "svchost.exe", "dwm.exe", "explorer.exe", "sihost.exe",
    "taskhostw.exe", "fontdrvhost.exe", "runtimebroker.exe", "taskmgr.exe",
    "cmd.exe", "powershell.exe", "pwsh.exe", "windowsterminal.exe", "openconsole.exe",
    "conhost.exe", "python.exe", "pythonw.exe", "py.exe", "codex.exe", "chatgpt.exe",
    "securityhealthservice.exe", "securityhealthsystray.exe", "msmpeng.exe",
    "shellexperiencehost.exe", "startmenuexperiencehost.exe", "searchhost.exe",
    "applicationframehost.exe", "systemsettings.exe", "lockapp.exe", "userinit.exe",
}

READ_WINDOWS = r"""
$session = (Get-Process -Id $PID).SessionId
$items = @(Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.SessionId -eq $session } |
    ForEach-Object {
        try {
            [pscustomobject]@{ pid = $_.Id; ticks = [string]$_.StartTime.ToUniversalTime().Ticks }
        } catch { }
    })
ConvertTo-Json -InputObject $items -Compress
"""

CLOSE_WINDOW = r"""
$process = Get-Process -Id ([int]$data.pid)
if ([string]$process.StartTime.ToUniversalTime().Ticks -ne [string]$data.ticks) {
    throw 'The process identity changed. Refresh the application list.'
}
if ($process.SessionId -ne (Get-Process -Id $PID).SessionId) {
    throw 'The application is no longer in your session.'
}
$process.CloseMainWindow() | ConvertTo-Json -Compress
"""


# Python OOP - Classes
class MemoryTool:
    # Python Functions, Arguments and Return Values
    def __init__(self, store):
        self.store = store

    def run(self):
        # Python Data Structures - Tuple
        # Python Data Structures - Dictionary
        run_menu("RAM CLEANUP", {
            "1": ("Show current physical memory", self.show_memory),
            "2": ("Show memory-heavy user apps and request one to close", self.close_app),
        })

    def show_memory(self):
        memory = psutil.virtual_memory()
        # Python Arithmetic Operations
        used = memory.total - memory.available
        # Python String Operations
        print(f"Total: {format_bytes(memory.total)} | Used: {format_bytes(used)} | "
              f"Available: {format_bytes(memory.available)} ({memory.percent:.1f}% used)")
        return memory

    def eligible(self, process, username, protected_pids):
        # Exception Handling in Python
        try:
            # Python Flow Control - Conditionals
            if process.pid in protected_pids or process.name().casefold() in BLOCKED_NAMES:
                return False
            if process.username().casefold() != username.casefold():
                return False
            executable = process.exe()
            if not executable:
                return False
            system_root = Path(os.environ.get("SystemRoot", r"C:\Windows")).resolve()
            if Path(executable).resolve().is_relative_to(system_root):
                return False
            return not is_critical_process(process.pid)
        except (psutil.Error, OSError):
            return False

    def applications(self):
        gui_apps = powershell_json(READ_WINDOWS)
        if not isinstance(gui_apps, list):
            raise ToolError("Windows did not return a user application list.")
        current = psutil.Process()
        username = current.username()
        protected_pids = {current.pid}
        # Python Flow Control - Loops
        for parent in current.parents():
            protected_pids.add(parent.pid)
        # Python Data Structures - List
        applications = []
        for window in gui_apps:
            try:
                process = psutil.Process(int(window["pid"]))
                if self.eligible(process, username, protected_pids):
                    applications.append({"pid": process.pid, "name": process.name(),
                                         "created": process.create_time(), "ticks": window["ticks"],
                                         "rss": process.memory_info().rss})
            except psutil.Error:
                continue
        # Python Lambda Functions
        applications.sort(key=lambda app: app["rss"], reverse=True)
        return applications[:15]

    # Python Decorators
    @logged_action
    def close_app(self):
        self.show_memory()
        print("Listing up to 15 eligible apps with a main window, owned by you in this session.")
        print("Windows processes, critical processes, shells, and this app's parents are excluded.")
        apps = self.applications()
        if not apps:
            print("No eligible apps were found. Access restrictions can also hide applications.")
            return "no eligible apps"
        for number, app in enumerate(apps, start=1):
            print(f"{number}. {app['name']} (PID {app['pid']}): {format_bytes(app['rss'])} resident")
        print("This is the main process's working set; shared memory and helper processes affect totals.")
        choice = read_number("Application number (0 to cancel): ", 0, len(apps))
        if not choice:
            return "cancelled"
        app = apps[choice - 1]
        print("Save your work first. Closing an application can lose unsaved work or close multiple windows.")
        print("The app may show a save dialog or decline to close. It will not be force-killed.")
        if not confirm(f"Request {app['name']} (PID {app['pid']}) to close?"):
            return "cancelled"
        fresh = next((item for item in self.applications() if item["pid"] == app["pid"]
                      and item["created"] == app["created"] and item["ticks"] == app["ticks"]), None)
        if fresh is None:
            raise ToolError("The application exited or is no longer eligible. Refresh the list.")
        process = psutil.Process(app["pid"])
        before = psutil.virtual_memory()
        sent = powershell_json(CLOSE_WINDOW, {"pid": app["pid"], "ticks": app["ticks"]})
        if sent is not True:
            print("The close request was declined or no enabled main window was available.")
            return "close request declined"
        try:
            process.wait(timeout=5)
            outcome = "application exited"
            print("The application exited.")
        except psutil.TimeoutExpired:
            outcome = "close requested; app still running"
            print("The application is still running. Check its save dialog; no forced close will be attempted.")
        after = self.show_memory()
        difference = after.available - before.available
        print(f"Observed available-memory change: {format_bytes(difference)}")
        print("Other activity also changes memory use. Windows manages RAM; no speed improvement is promised.")
        return outcome
