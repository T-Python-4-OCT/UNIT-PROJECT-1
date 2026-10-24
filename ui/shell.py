import shlex

from utils.errors import ClinicError, UsageError
from utils.formatters import table


def print_help(commands):
    rows = [(usage, desc) for _, usage, desc in commands.values()]
    rows += [("help", "Show this list"), ("logout", "Return to the main menu"),
             ("exit", "Quit the program")]
    print(table(["Command", "Description"], rows))


def run_shell(user, commands):
    """Generic command loop. Returns 'logout' or 'exit'."""
    print("Type 'help' to see the available commands.\n")
    while True:
        try:
            line = input(f"{user.username}@clinic > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "exit"
        if not line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            print("❌ Unbalanced quotes in command.")
            continue

        cmd, args = parts[0].lower(), parts[1:]
        if cmd == "help":
            print_help(commands)
        elif cmd == "logout":
            print("👋 Logged out.\n")
            return "logout"
        elif cmd == "exit":
            return "exit"
        elif cmd in commands:
            handler, usage, _ = commands[cmd]
            try:
                handler(user, args)
            except UsageError:
                print(f"Usage: {usage}")
            except ClinicError as e:
                print(f"❌ {e}")
        else:
            print(f"❌ Unknown command '{cmd}'. Type 'help'.")