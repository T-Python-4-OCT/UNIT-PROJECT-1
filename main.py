# Python Modules and Packages
import argparse
import os
from pathlib import Path
import sys


# Python Functions, Arguments and Return Values
def main(arguments=None):
    # Python Flow Control - Conditionals
    if os.name != "nt":
        print("System Toolkit supports Windows 10/11 only.")
        return 1
    # Python Data Structures - Tuple
    if sys.version_info < (3, 11):
        print("Please use Python 3.11 or newer.")
        return 1
    # Exception Handling in Python
    try:
        from toolkit.app import ToolkitApp
        from toolkit.windows import is_admin

        parser = argparse.ArgumentParser(description="System Toolkit for Windows")
        parser.add_argument("--admin-action", choices=("dns-change", "dns-automatic", "dns-restore", "dns-cache"),
                            help=argparse.SUPPRESS)
        parser.add_argument("--settings-dir", help=argparse.SUPPRESS)
        options = parser.parse_args(arguments)
        if options.admin_action:
            if not options.settings_dir or not Path(options.settings_dir).is_absolute():
                raise ValueError("Administrator actions require the original settings folder.")
            if not is_admin():
                print("Windows did not grant administrator access. No action was run.")
                return 1
        elif options.settings_dir:
            raise ValueError("A settings folder can only be supplied with an administrator action.")
        ToolkitApp(options.settings_dir).run(admin_action=options.admin_action)
    except ModuleNotFoundError as error:
        # Python String Operations
        print(f"Missing package: {error.name}")
        print(r"Install dependencies: .\.venv\Scripts\python.exe -m pip install -r requirements.txt")
        return 1
    except (OSError, ValueError) as error:
        print(f"Cannot start safely: {error}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
