import sys
import time
from contextlib import contextmanager

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()

CYAN = "#19b5ff"
DIM = "#0e86c2"
GREEN = "#28d17c"
YELLOW = "#ffd23f"
RED = "#ff4258"
VIOLET = "#b57bff"

WEATHER_CODES = {
    0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"), 45: ("Fog", "🌫️"), 48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌦️"), 63: ("Rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
    71: ("Light snow", "🌨️"), 73: ("Snow", "🌨️"), 75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"), 81: ("Rain showers", "🌧️"), 82: ("Violent showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm, hail", "⛈️"), 99: ("Thunderstorm, hail", "⛈️"),
}


def clear():
    console.clear()


def title(text):
    """'--- Manager Dashboard (admin) ---' heading."""
    console.print(f"\n[bold {CYAN}]--- {text} ---[/]")


def heading(icon, text, color=VIOLET):
    console.print(f"\n{icon} [bold {CYAN}]{text}[/]" if color is None else f"\n{icon} [bold {color}]{text}[/]")


def ok(msg):
    console.print(f"[bold {GREEN}]✅ {msg}[/]")


def error(msg):
    console.print(f"[bold {RED}]❌ {msg}[/]")


def info(msg):
    console.print(f"[{CYAN}]{msg}[/]")


def ask(label):
    return console.input(f"[{CYAN}]{label}[/] ").strip()


_raw_depth = 0


@contextmanager
def raw_input():
    """Put the terminal in single-key mode while active (no-op on Windows / non-terminals).
    Held for the whole menu so keys typed quickly are not lost between reads."""
    global _raw_depth
    if sys.platform == "win32" or not sys.stdin.isatty() or _raw_depth > 0:
        yield                                            
        return
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd, termios.TCSADRAIN)                 
    try:
        yield
    finally:
        _raw_depth -= 1
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def read_key():
    """Read one key press without Enter.
    Returns 'UP', 'DOWN', 'ENTER', 'ESC' or the typed character ('' if unknown)."""
    try:
        if sys.platform == "win32":
            import msvcrt
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):                 
                return {"H": "UP", "P": "DOWN"}.get(msvcrt.getwch(), "")
            if ch == "\x03":
                raise KeyboardInterrupt
            return {"\r": "ENTER", "\x1b": "ESC"}.get(ch, ch)

        import os
        import select
        with raw_input():
            fd = sys.stdin.fileno()
            ch = os.read(fd, 1).decode(errors="ignore")
            if ch == "\x1b":
                if select.select([fd], [], [], 0.05)[0]:
                    seq = os.read(fd, 2).decode(errors="ignore")
                    return {"[A": "UP", "[B": "DOWN", "OA": "UP", "OB": "DOWN"}.get(seq, "")
                return "ESC"
            return "ENTER" if ch in ("\r", "\n") else ch
    except (ImportError, OSError, ValueError):
        input()                                         
        return "ENTER"


def ask_password(label="Password:"):
    """Like getpass, but shows one '*' per typed character (Backspace works)."""
    console.print(f"[{CYAN}]{label}[/] ", end="")
    if not (sys.stdin.isatty() and console.is_terminal):
        import getpass
        return getpass.getpass("")
    chars = []
    with raw_input():
        while True:
            key = read_key()
            if key == "ENTER":
                break
            if key in ("\x7f", "\x08"):                 
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
            elif len(key) == 1 and key.isprintable():
                chars.append(key)
                sys.stdout.write("*")
            sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()
    return "".join(chars)


def getch():
    return read_key()


def pause():
    console.print(f"\n[{CYAN}]Press any key to go back...[/]")
    read_key()


def select(heading_text, options, prompt="Choose an option"):
    """Arrow-key menu. Up/Down move the highlight, Enter selects, and typing a
    number jumps to that option. Returns the chosen index (0-based), or -1 if
    the fallback (non-interactive) input was invalid."""
    n = len(options)
    if heading_text:
        title(heading_text)
    interactive = sys.stdin.isatty() and console.is_terminal
    if not interactive:
        for i, label in enumerate(options, 1):
            console.print(f" {i}.  {label}")
        raw = ask(f"{prompt} (1-{n}):")
        if not raw:
            return 0
        return int(raw) - 1 if raw.isdigit() and 1 <= int(raw) <= n else -1

    def render(idx, done=False):
        lines = [Text("")]
        for i, label in enumerate(options):
            if i == idx:
                lines.append(Text(f" {i + 1}.  {label:<62}", style=f"bold #021320 on {CYAN}"))
            else:
                lines.append(Text.assemble((f" {i + 1}.  ", "dim"), label))
        lines.append(Text(""))
        lines.append(Text("─" * 70, style=DIM))
        tail = Text.assemble((f"{prompt} (1-{n}): ", CYAN), (str(idx + 1), "bold"))
        if not done:
            tail.append("   ↑/↓ move · Enter select", style="dim")
        lines.append(tail)
        return Group(*lines)

    idx = 0
    with raw_input(), Live(render(idx), console=console, auto_refresh=False) as live:
        while True:
            key = read_key()
            if key == "UP":
                idx = (idx - 1) % n
            elif key == "DOWN":
                idx = (idx + 1) % n
            elif key == "ENTER":
                break
            elif key.isdigit() and 1 <= int(key) <= n:
                idx = int(key) - 1
            live.update(render(idx), refresh=True)
        live.update(render(idx, done=True), refresh=True)
    return idx


def menu(heading_text, options):
    """Same as select(), but returns the choice as a '1'-based string."""
    idx = select(heading_text, options)
    return str(idx + 1) if idx >= 0 else ""


def display_header():
    t = Text.assemble(("🚨 CRISIS MANAGEMENT & LOGISTICS SIMULATOR 🚨", f"bold {RED}"))
    sub = Text("Secure Emergency Response & Fleet Dispatch Command Center", style=CYAN)
    console.print(Panel(Align.center(Group(Align.center(t), Align.center(sub))),
                        border_style=CYAN, box=box.DOUBLE, padding=(1, 2)))


def password_rules_notice():
    console.print(Panel(
        Text.assemble(("🔑 Password rules\n", f"bold {YELLOW}"),
                      ("• At least 8 characters\n• At least one UPPERCASE letter (A-Z)\n• At least one lowercase letter (a-z)", "")),
        border_style=YELLOW, width=48, padding=(0, 2)))


def login_panel():
    """Draws the login box. The caller then prompts for the fields."""
    body = Group(
        Align.center(Text("Login", style=f"bold {CYAN}")),
        Text(""),
        Text("👤 Username", style="dim"),
        Text("🔒 Password (hidden while typing)", style="dim"),
    )
    console.print(Panel(body, border_style=CYAN, width=58, padding=(1, 2)))


def _table(title_text, icon, **kw):
    return Table(
        title=f"{icon} [bold {VIOLET}]{title_text}[/]", title_justify="left",
        border_style=DIM, header_style=f"bold {CYAN}", box=box.SQUARE, **kw,
    )


def status_badge(status):
    s = (status or "").lower()
    if "completed" in s:
        return Text(" Completed ", style="bold white on #1e9e5a")
    if "transit" in s:
        return Text(" Transit ", style="bold white on #1e9e5a")
    if "approved" in s:
        return Text(" Approved ", style="bold white on #1590e8")
    return Text(" Pending ", style="bold #2a2200 on " + YELLOW)


def display_supplies_table(supplies):
    table = _table("Emergency Supplies Inventory", "📦")
    table.add_column("ID", justify="center", style=CYAN)
    table.add_column("Name")
    table.add_column("Category", style=GREEN)
    table.add_column("Quantity", justify="right")
    table.add_column("Unit Weight (kg)", justify="right", style="#4aa3ff")
    for item in supplies:
        try:
            qty = int(item.get("quantity") or 0)
        except (TypeError, ValueError):
            qty = 0
        qty_cell = f"[{RED}]{qty} (Low)[/]" if qty < 10 else f"[{YELLOW}]{qty}[/]"
        weight = item.get("unit_weight_kg") or item.get("unit_weight") or 0.0
        table.add_row(str(item.get("id") or item.get("item_id") or "N/A"),
                      str(item.get("name") or "Unknown"),
                      str(item.get("category") or "General"), qty_cell, f"{float(weight):.2f}")
    console.print(table)


def display_shipments_table(shipments):
    table = _table("Active Shipments & Tracking", "🚚")
    for col, kw in [("Shipment ID", {"style": CYAN}), ("Item", {}), ("Quantity", {"justify": "right"}),
                    ("Destination", {}), ("Vehicle", {}), ("Status", {"justify": "center"})]:
        table.add_column(col, **kw)
    for s in shipments:
        vehicle = s.get("vehicle")
        veh = Text(vehicle) if vehicle else Text("Unassigned", style=RED)
        table.add_row(str(s.get("shipment_id")), str(s.get("item_name", "—")), str(s.get("quantity", 0)),
                      str(s.get("destination") or "—").title(), veh, status_badge(s.get("status")))
    console.print(table)


def display_field_requests_table(requests):
    table = _table("Field Supervisor Requests & Status", "📋")
    for col, kw in [("ID", {"style": CYAN}), ("Region", {}), ("Item", {}),
                    ("Quantity", {"justify": "right"}), ("Priority", {}), ("Status", {"justify": "center"})]:
        table.add_column(col, **kw)
    colors = {"High": f"bold {RED}", "Medium": f"bold {YELLOW}", "Low": f"bold {GREEN}"}
    for r in requests:
        pr = r.get("priority", "Medium")
        table.add_row(str(r.get("request_id")), str(r.get("zone") or "—").title(), str(r.get("item_name")),
                      str(r.get("quantity")), Text(pr, style=colors.get(pr, "")), status_badge(r.get("status")))
    console.print(table)


def display_users_table(users):
    table = _table("Registered System Users", "👥")
    for col in ["#", "User", "Role", "Email"]:
        table.add_column(col)
    for i, u in enumerate(users, 1):
        table.add_row(str(i), f"[{CYAN}]{u.get('user_name', 'Unknown')}[/]",
                      f"[{GREEN}]{u.get('role', 'general')}[/]", u.get("email", "N/A"))
    console.print(table)


def display_recommendations(recs, category):
    table = Table(border_style=DIM, header_style=f"bold {CYAN}", box=box.SQUARE, expand=True)
    for col, kw in [("#", {"justify": "right"}), ("Item", {}), ("Category", {}), ("In stock", {"justify": "right"})]:
        table.add_column(col, **kw)
    for i, r in enumerate(recs, 1):
        table.add_row(str(i), str(r.get("name")), str(r.get("category")), str(r.get("quantity")))
    console.print(Panel(table, title=f"[bold {GREEN}]Smart Recommendations: {category}[/]",
                        title_align="left", border_style=GREEN))


def weather_panel(region_name, weather):
    text, emoji = WEATHER_CODES.get(weather.get("weathercode"), ("Unknown", "🌡️"))
    grid = Table.grid(padding=(0, 3))
    grid.add_column(); grid.add_column()
    grid.add_row(Text(emoji + "  ", style="bold"), Group(
        Text(f"Weather in {region_name}", style=f"bold {YELLOW}"),
        Text.assemble(("Temperature:  ", "dim"), f"{weather.get('temperature')}°C"),
        Text.assemble(("Wind Speed:   ", "dim"), f"{weather.get('windspeed')} km/h"),
        Text.assemble(("Condition:    ", "dim"), text),
    ))
    console.print(Panel(grid, border_style=CYAN, padding=(1, 3)))


class ColoredBar(BarColumn):
    """Progress bar whose color comes from task.fields['color']."""
    def render(self, task):
        self.complete_style = self.finished_style = task.fields.get("color", CYAN)
        return super().render(task)


def simulate_dispatch_progress(shipment_id, vehicle=None, destination=None):
    console.print(f"\n🚚 [bold {YELLOW}]Initializing dispatch protocols for shipment {shipment_id}...[/]\n")
    steps = [
        ("🛡️  Verifying transport route safety...", CYAN, 15),
        (f"📦 Loading cargo onto {vehicle or 'assigned vehicle'}...", GREEN, 20),
        (f"📍 Dispatched successfully to {destination or 'destination zone'}...", "#ff62d6", 25),
    ]
    with Progress(TextColumn("{task.description}"), ColoredBar(bar_width=None),
                  TextColumn("[bold]{task.percentage:>3.0f}%"), console=console, expand=True) as progress:
        tasks = [progress.add_task(f"[{c}]{d}[/]", total=100, color=c) for d, c, _ in steps]
        for (_, _, step), tid in zip(steps, tasks):
            while not progress.tasks[tid].finished:
                progress.update(tid, advance=step)
                time.sleep(0.12)
    console.print(Panel(Text.assemble(("✅  ", ""), (f"✨ Shipment {shipment_id} is successfully on the move and tracked by command!", f"bold {GREEN}")),
                        border_style=GREEN, padding=(1, 2)))