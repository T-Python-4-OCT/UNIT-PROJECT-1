def banner():
    lines = ["SmartClinic Reception  v1.0", "Clinic front-desk, managed in terminal"]
    out = ["╔" + "═" * 42 + "╗"]
    out += ["║" + text.center(42) + "║" for text in lines]
    out.append("╚" + "═" * 42 + "╝")
    return "\n".join(out)


def table(headers, rows):
    """Render a simple box-drawing table."""
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


def _money_line(label, amount, width):
    left = f" {label} "
    right = f" {amount:.2f} SAR"
    dots = "." * max(width - len(left) - len(right), 2)
    return left + dots + right


def invoice_text(inv):
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