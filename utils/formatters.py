"""Text formatting helpers.

Uses the `rich` library for colours and nicer tables when it is installed,
and falls back to plain text when it is not (the program still works).
"""
try:
    from rich import box
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.table import Table
    from rich.text import Text

    RICH = True
    _console = Console()
except ImportError:          # rich is not installed -> plain output
    RICH = False

# colour of each appointment status inside tables
STATUS_STYLES = {"booked": "yellow", "checked_in": "cyan",
                 "completed": "green", "cancelled": "red"}


# ---------------------------------------------------------------- rich helpers
def _render(renderable):
    """Render a rich object to a string (so callers can keep using print())."""
    with _console.capture() as cap:
        _console.print(renderable)
    return cap.get().rstrip("\n")


def paint(text, style):
    """Colour a piece of text, e.g. paint('Done', 'green'). Plain text without rich."""
    if not RICH:
        return text
    return _render(Text(text, style=style))


# ---------------------------------------------------------------- banner
def _plain_banner():
    lines = ["SmartClinic Reception  v1.0", "Clinic front-desk, managed in terminal"]
    out = ["╔" + "═" * 42 + "╗"]
    out += ["║" + text.center(42) + "║" for text in lines]
    out.append("╚" + "═" * 42 + "╝")
    return "\n".join(out)


def _rich_banner():
    body = Text.assemble(("SmartClinic Reception  v1.0\n", "bold white"),
                         ("Clinic front-desk, managed in terminal", "dim"),
                         justify="center")
    return _render(Panel(body, box=box.DOUBLE, border_style="cyan",
                         expand=False, padding=(0, 4)))


def banner():
    return _rich_banner() if RICH else _plain_banner()


# ---------------------------------------------------------------- table
def _plain_table(headers, rows):
    headers = [str(h) for h in headers]
    rows = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def line(left, mid, right):
        return left + mid.join("─" * (w + 2) for w in widths) + right

    def fmt(cells):
        return "│" + "│".join(f" {c.ljust(w)} " for c, w in zip(cells, widths)) + "│"

    out = [line("┌", "┬", "┐"), fmt(headers), line("├", "┼", "┤")]
    out += [fmt(r) for r in rows]
    out.append(line("└", "┴", "┘"))
    return "\n".join(out)


def _rich_table(headers, rows):
    t = Table(box=box.ROUNDED, header_style="bold cyan")
    for h in headers:
        t.add_column(str(h))
    for row in rows:
        # Text(...) is used so characters like [ ] in names are never treated as markup
        t.add_row(*[Text(str(c), style=STATUS_STYLES.get(str(c), "")) for c in row])
    return _render(t)


def table(headers, rows):
    """Render a table (coloured with rich, or plain box-drawing)."""
    return _rich_table(headers, rows) if RICH else _plain_table(headers, rows)


# ---------------------------------------------------------------- invoice
def _money_line(label, amount, width):
    left = f" {label} "
    right = f" {amount:.2f} SAR"
    dots = "." * max(width - len(left) - len(right), 2)
    return left + dots + right


def _plain_invoice(inv):
    width = 47
    appt, patient, clinic = inv["appointment"], inv["patient"], inv["clinic"]
    out = [f" INVOICE #{appt.id} ".center(width, "═")]
    out.append(f" Patient : {patient.full_name}")
    out.append(f" Clinic  : {clinic.name} ({clinic.doctor})")
    out.append(f" Date    : {appt.date}")
    out.append("─" * width)
    for label, amount in inv["lines"]:
        out.append(_money_line(label, amount, width))
    out.append("─" * width)
    out.append(_money_line("VAT (15%)", inv["vat"], width))
    out.append(_money_line("TOTAL", inv["total"], width))
    out.append("═" * width)
    return "\n".join(out)


def _rich_invoice(inv):
    appt, patient, clinic = inv["appointment"], inv["patient"], inv["clinic"]
    info = Text.assemble(("Patient : ", "bold"), f"{patient.full_name}\n",
                         ("Clinic  : ", "bold"), f"{clinic.name} ({clinic.doctor})\n",
                         ("Date    : ", "bold"), appt.date)
    money = Table.grid(expand=True)
    money.add_column()
    money.add_column(justify="right")
    for label, amount in inv["lines"]:
        money.add_row(label, f"{amount:.2f} SAR")
    money.add_row("VAT (15%)", f"{inv['vat']:.2f} SAR")
    money.add_row(Text("TOTAL", style="bold green"),
                  Text(f"{inv['total']:.2f} SAR", style="bold green"))
    return _render(Panel(Group(info, Rule(style="dim"), money),
                         title=f"INVOICE #{appt.id}", box=box.DOUBLE,
                         border_style="green", width=50))


def invoice_text(inv):
    return _rich_invoice(inv) if RICH else _plain_invoice(inv)