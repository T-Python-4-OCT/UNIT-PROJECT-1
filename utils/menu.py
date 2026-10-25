import os
import sys

from colorama import Fore, Style

from utils import display, validators


def read_key():
    """Wait for one key press. Return 'up', 'down', 'enter', 'other', or the typed character."""
    if os.name == "nt":
        import msvcrt

        char = msvcrt.getwch()
        if char in ("\x00", "\xe0"):  # arrow keys send two codes on Windows
            return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "other")
        if char in ("\r", "\n"):
            return "enter"
        if char == "\x03":  # Ctrl+C
            raise KeyboardInterrupt
        return char

    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd, termios.TCSANOW)
        char = os.read(fd, 1).decode(errors="ignore")
        if char == "\x1b":  # arrow keys send: ESC [ A  or  ESC [ B
            rest = os.read(fd, 2).decode(errors="ignore")
            return {"[A": "up", "[B": "down", "OA": "up", "OB": "down"}.get(rest, "other")
        if char in ("\r", "\n"):
            return "enter"
        return char
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class Menu:
    """A menu the user can navigate with the Up/Down arrows and Enter.

    If the terminal cannot read single key presses (for example when the input
    is piped), it falls back to asking the user to type the option number.
    """

    def __init__(self, title, options):
        self.title = title
        self.options = list(options)  # list of (key, label), for example ("1", "Manage Farm")

    def choose(self):
        """Show the menu and return the key of the option the user selected."""
        display.print_title(self.title)
        if sys.stdin.isatty() and sys.stdout.isatty():
            try:
                return self._choose_with_arrows()
            except (ImportError, OSError):
                pass  # the terminal does not support it; use typing instead
        return self._choose_by_typing()

    def _choose_by_typing(self):
        for key, label in self.options:
            print(f"{key}. {label}")
        keys = [key for key, _ in self.options]
        return validators.get_menu_choice("Enter your choice: ", keys)

    def _choose_with_arrows(self):
        print("Use the Up/Down arrow keys and press Enter.")
        shortcuts = {key: index for index, (key, _) in enumerate(self.options) if len(key) == 1}
        selected = 0
        self._draw(selected, redraw=False)
        while True:
            pressed = read_key()
            if pressed == "up":
                selected = (selected - 1) % len(self.options)
            elif pressed == "down":
                selected = (selected + 1) % len(self.options)
            elif pressed == "enter":
                return self.options[selected][0]
            elif pressed in shortcuts:  # typing the option number still works
                return self.options[shortcuts[pressed]][0]
            self._draw(selected, redraw=True)

    def _draw(self, selected, redraw):
        """Print all options, highlighting the selected one. Redraw in place if needed."""
        if redraw:
            sys.stdout.write(f"\x1b[{len(self.options)}A")  # move the cursor back to the first option
        for index, (key, label) in enumerate(self.options):
            if index == selected:
                line = Fore.CYAN + Style.BRIGHT + f"> {key}. {label}"
            else:
                line = f"  {key}. {label}"
            sys.stdout.write("\x1b[2K" + line + "\n")  # clear the line, then write it
        sys.stdout.flush()