"""General settings of the app."""

APP_NAME = "VOX CINEMAS - RIYADH"

# Booking rules
MAX_SEATS_PER_BOOKING = 6
SHOW_DAYS_AHEAD = 7  # seven days starting today
SHOW_TIMES = ("13:30", "16:00", "19:15", "22:30")  # tuple: these never change

# Files and folders
DATA_DIR = "data"
BOOKINGS_FILE = "data/bookings.json"
TICKETS_DIR = "tickets"

