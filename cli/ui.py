"""Terminal UI built on the `rich` library: colors, boxes, tables, numbered menus."""
from rich import box as rich_box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


# ---------- colors (rich markup) ----------
def green(text):
    return f"[green]{text}[/green]"


def red(text):
    return f"[red]{text}[/red]"


def yellow(text):
    return f"[yellow]{text}[/yellow]"


def bold(text):
    return f"[bold]{text}[/bold]"


def esc(text):
    """Escape text typed by the user so rich does not read it as markup."""
    return escape(str(text))


def success(text):
    console.print(green(esc(text)))


def error(text):
    console.print(red(esc(text)))


# ---------- boxes and tables ----------
def _plain_len(markup_text):
    """Length of a text without its [color] tags."""
    return len(Text.from_markup(markup_text).plain)


def box(lines, title=None, min_width=34):
    """Print lines inside a square box (with an optional centered title)."""
    longest = max([min_width] + [_plain_len(l) for l in lines]
                  + ([_plain_len(title)] if title else []))
    console.print(Panel(
        "\n".join(lines),
        title=bold(title) if title else None,
        title_align="center",
        box=rich_box.SQUARE,
        border_style="cyan",
        width=longest + 4,   # +2 borders, +2 padding
    ))


def table(headers, rows, title=None):
    """Print a boxed table. `rows` is a list of lists (cells may use color markup)."""
    if not rows:
        box(["Nothing to show."], title)
        return
    grid = Table(title=title, box=rich_box.SQUARE, border_style="cyan",
                 header_style="bold", title_style="bold")
    for header in headers:
        grid.add_column(header)
    for row in rows:
        grid.add_row(*[str(cell) for cell in row])
    console.print(grid)


# ---------- input ----------
def ask_int(prompt, low, high):
    """Ask until the user types a whole number between low and high."""
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and low <= int(raw) <= high:
            return int(raw)
        error(f"Please type a number between {low} and {high}.")


def ask_valid(prompt, validator):
    """Ask until `validator` accepts the text (it raises ValueError if bad)."""
    while True:
        try:
            return validator(input(prompt).strip())
        except ValueError as err:
            error(f"Error: {err}")


def menu(title, options, back_label="Back", available=None):
   
    lines = []
    for i, label in enumerate(options, 1):
        text = f"{i}. {label}"
        if available is not None:
            text = green(text) if available[i - 1] else red(text)
        lines.append(text)
    lines.append(f"0. {back_label}")

    console.print()
    box(lines, title)
    if available is not None:
        console.print(green("■ available") + "   " + red("■ not available"))

    while True:
        choice = ask_int("Your choice: ", 0, len(options))
        if choice == 0:
            return None
        if available is not None and not available[choice - 1]:
            error("That option is not available. Please choose a green one.")
            continue
        return choice - 1


def confirm(question):
    """Yes/No question. Returns True for yes."""
    return menu(question, [green("Yes")], red("No")) == 0
