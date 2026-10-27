# Python Modules and Packages
import pythoncom
import pywintypes
from win32com.server.exception import COMException
from win32com.shell import shell, shellcon

from send2trash.win.IFileOperationProgressSink import FileOperationProgressSink


# Python OOP - Classes
class RecycleOnlySink(FileOperationProgressSink):
    # Python Functions, Arguments and Return Values
    def PreDeleteItem(self, flags, item):
        # Python Flow Control - Conditionals
        if not flags & shellcon.TSF_DELETE_RECYCLE_IF_POSSIBLE:
            raise COMException(desc="This tool only supports recycling.", scode=-2147467260)
        return 0


def recycle_file(path):
    initialized = False
    # Exception Handling in Python
    try:
        pythoncom.CoInitialize()
        initialized = True
        operation = pythoncom.CoCreateInstance(
            shell.CLSID_FileOperation, None, pythoncom.CLSCTX_ALL, shell.IID_IFileOperation
        )
        flags = (shellcon.FOF_SILENT | shellcon.FOF_NOCONFIRMATION | shellcon.FOF_NOERRORUI
                 | shellcon.FOF_NO_CONNECTED_ELEMENTS | 0x00080000 | 0x20000000 | 0x00100000)
        operation.SetOperationFlags(flags)
        sink = pythoncom.WrapObject(RecycleOnlySink(), shell.IID_IFileOperationProgressSink)
        item = shell.SHCreateItemFromParsingName(str(path), None, shell.IID_IShellItem)
        operation.DeleteItem(item, sink)
        result = operation.PerformOperations()
        if result or operation.GetAnyOperationsAborted():
            raise OSError("Windows could not complete the recycling request.")
    except pywintypes.com_error as error:
        # Python String Operations
        raise OSError(f"Windows could not recycle this file: {error.strerror}") from error
    finally:
        if initialized:
            pythoncom.CoUninitialize()
