from rich.text import Text

from . import ui
from .pricing import NORTH_ROWS, PRICES, ROW_CATEGORY, SOUTH_ROWS

GREEN = "bold black on green"
YELLOW = "bold black on yellow"
RED = "bold white on red"
PITCH = "bold white on green"

WIDTH = 90
LEFT = 6
BLOCK = 64            

def _cell(seat, booked, held):
    if seat in booked:
        style = RED
    elif seat in held:
        style = YELLOW
    else:
        style = GREEN
    return f" {seat:^3} ", style


def _block(row, numbers, booked, held):
    line = Text()
    for number in numbers:
        text, style = _cell(f"{row}{number}", booked, held)
        line.append(text, style=style)
        line.append(" ")
    return line


def _stand_row(row, booked, held):
    """One row of 10 seats with an aisle in the middle, and its category on the right."""
    category = ROW_CATEGORY[row]
    line = Text(" " * LEFT + f"  {row} ", style="bold")
    line.append_text(_block(row, range(1, 6), booked, held))
    line.append("    ")
    line.append_text(_block(row, range(6, 11), booked, held))
    line.append(f"  {category} {PRICES[category]} SAR", style="dim")
    return line


def _pitch_grid(width, height=7):
    """A football pitch drawn with characters: center line and circle, penalty boxes, six-yard boxes and spots."""
    grid = [[" "] * width for _ in range(height)]
    middle = width // 2
    for r in range(height):
        grid[r][middle] = "|"
    for r, text in ((2, " .-. "), (3, "( o )"), (4, " '-' ")):
        for k, ch in enumerate(text):
            grid[r][middle - 2 + k] = ch

    def box(left, right, top, bottom):
        for c in range(left, right + 1):
            grid[top][c] = grid[bottom][c] = "-"
        for r in range(top, bottom + 1):
            grid[r][left] = grid[r][right] = "|"
        for r, c in ((top, left), (top, right), (bottom, left), (bottom, right)):
            grid[r][c] = "+"

    box(0, 9, 1, 5)                      # left penalty box
    box(0, 3, 2, 4)                      # left six-yard box
    box(width - 10, width - 1, 1, 5)     # right penalty box
    box(width - 4, width - 1, 2, 4)      # right six-yard box
    grid[3][6] = grid[3][width - 7] = "."          # penalty spots
    return ["".join(row) for row in grid]


def _pitch_lines():
    inner = BLOCK - 2
    pad = " " * (LEFT + 4)
    edge = Text(pad + "+" + "-" * inner + "+", style="bold white")
    lines = [edge]
    for number, text in enumerate(_pitch_grid(inner)):
        is_goal = 2 <= number <= 4                      # the goals are in the middle of the short sides
        side = "#" if is_goal else "|"
        line = Text(pad + side, style="bold yellow" if is_goal else "bold white")
        line.append(text, style=PITCH)
        line.append(side, style="bold yellow" if is_goal else "bold white")
        lines.append(line)
    lines.append(Text(edge.plain, style="bold white"))
    return lines


def _centered(text, style=""):
    return Text(text.center(WIDTH), style=style)


def draw_stadium(heading, booked, held):
    ui.console.print()
    ui.console.print(_centered(heading, "bold"))
    if ui.console.width < WIDTH + 2:
        ui.warn("Make your terminal window wider so the stadium is drawn correctly.")
    ui.console.print(_centered("NORTH STAND", "bold cyan"))
    for row in NORTH_ROWS:
        ui.console.print(_stand_row(row, booked, held))
    for line in _pitch_lines():
        ui.console.print(line)
    for row in SOUTH_ROWS:
        ui.console.print(_stand_row(row, booked, held))
    ui.console.print(_centered("SOUTH STAND", "bold cyan"))
    ui.console.print()
    legend = Text(" " * 20)
    legend.append("  Available  ", style=GREEN)
    legend.append("   ")
    legend.append("  Held 5 min  ", style=YELLOW)
    legend.append("   ")
    legend.append("  Booked  ", style=RED)
    ui.console.print(legend)
    ui.console.print()