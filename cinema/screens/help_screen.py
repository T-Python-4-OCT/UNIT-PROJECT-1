"""The 'How to use' screen."""

from cinema.ui.decorators import pause_after
from cinema.ui.display import clear_screen, print_title

HELP_TEXT = """
- Type the NUMBER of the option you want, then press Enter.
- Book a ticket : name -> cinema -> movie -> experience -> showtime -> seats.
- Seats         : type the row letter + seat number, example: B5 (b5 or B-5 also work).
                  Type Q to stop choosing seats.
                  Green = free, Red = booked, Yellow = your choice.
- Prices        : Standard A-D 40 SAR, E-F 60 SAR | IMAX 80 SAR | Suites 150 SAR.
- Save your INVOICE NUMBER: use it (or your full name) in 'My bookings'
  to view, change seats, cancel, or save the ticket as a text file.
- Press Ctrl+C at any time to close the program."""


@pause_after
def show_help() -> None:
    clear_screen()
    print_title("How To Use")
    print(HELP_TEXT)
