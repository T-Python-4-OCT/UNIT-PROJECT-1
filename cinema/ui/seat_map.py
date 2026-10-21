"""Draw the cinema screen and the seats as separate colored squares inside a box."""

from colorama import Back, Style

from cinema.models.hall import Hall

SQUARE = "  "     # one seat = 2 colored spaces (looks like a square)
GAP = "  "        # space between two seats
CELL_WIDTH = len(SQUARE) + len(GAP)
AISLE = "    "    # bigger space between seat groups


def color_square(background: str) -> str:
    """A colored square: green = free, red = booked, yellow = your choice."""
    return background + SQUARE + Style.RESET_ALL


def row_width(hall: Hall) -> int:
    aisles = 0
    for col in range(1, hall.cols):
        if hall.has_aisle_after(col):
            aisles += 1
    return 4 + hall.cols * CELL_WIDTH + aisles * len(AISLE)


def print_box_line(content: str, visible_length: int, box_width: int) -> None:
    """Print one line inside the big box, centered."""
    space = box_width - visible_length
    left = space // 2
    right = space - left
    print("│" + " " * left + content + " " * right + "│")


def print_screen(inner_width: int, box_width: int) -> None:
    screen_width = inner_width - 4
    print_box_line("", 0, box_width)
    print_box_line("┌" + "─" * screen_width + "┐", screen_width + 2, box_width)
    print_box_line("│" + "S C R E E N".center(screen_width) + "│", screen_width + 2, box_width)
    print_box_line("└" + "─" * screen_width + "┘", screen_width + 2, box_width)
    print_box_line("", 0, box_width)


def build_header(hall: Hall) -> str:
    """The seat numbers line: 1 2 3 4 ..."""
    header = "    "
    for col in range(1, hall.cols + 1):
        header += f"{col:<2}" + GAP
        if hall.has_aisle_after(col) and col < hall.cols:
            header += AISLE
    return header


def build_row(hall: Hall, row: str, booked: set[str], selected: set[str]) -> str:
    """One row of seats as separate colored squares."""
    line = f" {row}  "
    for col in range(1, hall.cols + 1):
        seat = f"{row}{col}"
        if seat in selected:
            line += color_square(Back.YELLOW)
        elif seat in booked:
            line += color_square(Back.RED)
        else:
            line += color_square(Back.GREEN)
        line += GAP
        if hall.has_aisle_after(col) and col < hall.cols:
            line += AISLE
    return line


def print_legend(hall: Hall) -> None:
    print(color_square(Back.GREEN) + " Available    "
          + color_square(Back.RED) + " Booked    "
          + color_square(Back.YELLOW) + " Your choice")
    print(f"Prices -> {hall.price_info()}")


def draw_seat_map(hall: Hall, booked: set[str], selected: set[str] | None = None) -> None:
    if selected is None:
        selected = set()
    inner_width = row_width(hall)
    box_width = inner_width + 8

    print("┌" + "─" * box_width + "┐")
    print_screen(inner_width, box_width)

    header = build_header(hall)
    print_box_line(header, len(header), box_width)
    for row in hall.row_labels():
        print_box_line("", 0, box_width)  # empty line so the squares do not touch
        divider = hall.row_divider(row)
        if divider:
            print_box_line(divider, len(divider), box_width)
            print_box_line("", 0, box_width)
        print_box_line(build_row(hall, row, booked, selected), inner_width, box_width)

    print_box_line("", 0, box_width)
    print("└" + "─" * box_width + "┘")
    print_legend(hall)
