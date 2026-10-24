"""General settings of the app."""

APP_NAME = "VOX CINEMAS - RIYADH"

# Booking rules
MAX_SEATS_PER_BOOKING = 6
FIRST_SHOW_DAY = "2026-10-21"  # bookings are open from 21 October
LAST_SHOW_DAY = "2026-10-31"   # ... to 31 October
SHOW_TIMES = ("13:30", "16:00", "19:15", "22:30")  # tuple: these never change

# Files and folders
DATA_DIR = "data"
BOOKINGS_FILE = "data/bookings.json"
TICKETS_DIR = "tickets"

# City used for the weather forecast (Open-Meteo API)
CITY_NAME = "Riyadh"
CITY_LATITUDE = 24.71
CITY_LONGITUDE = 46.68
