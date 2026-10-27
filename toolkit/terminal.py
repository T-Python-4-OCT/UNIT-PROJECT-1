# Python Modules and Packages
import ctypes
from ctypes import wintypes
import os
import sys


# Python Functions, Arguments and Return Values
def console_text(text, fallback):
    try:
        if not sys.stdout.isatty():
            return fallback
        text.encode(sys.stdout.encoding or "ascii")
    except (AttributeError, LookupError, UnicodeError):
        return fallback
    return text


def supports_color():
    if not sys.stdout.isatty() or "NO_COLOR" in os.environ or os.environ.get("TERM") == "dumb":
        return False
    if os.name != "nt":
        return True
    try:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetStdHandle.argtypes = (wintypes.DWORD,)
        kernel.GetStdHandle.restype = wintypes.HANDLE
        kernel.GetConsoleMode.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.GetConsoleMode.restype = wintypes.BOOL
        kernel.SetConsoleMode.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        kernel.SetConsoleMode.restype = wintypes.BOOL
        handle = kernel.GetStdHandle(-11)
        mode = wintypes.DWORD()
        return bool(kernel.GetConsoleMode(handle, ctypes.byref(mode))
                    and kernel.SetConsoleMode(handle, mode.value | 0x0004))
    except (AttributeError, OSError):
        return False


def new_badge():
    badge = console_text("🚨 NEW", "[NEW]")
    return f"\033[31m{badge}\033[0m" if supports_color() else badge
