import os

RESTAURANT_NAME = "Majlis Table"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

BOOKING_DURATION_MINUTES = 90   
SLOT_STEP_MINUTES = 30         
BOOKING_WINDOW_DAYS = 7         
OPENING_HOUR = 12               
CLOSING_HOUR = 23               

LOCATIONS = ["indoor", "outdoor", "family", "vip"]


MANAGER_PASSWORD = os.environ.get("MANAGER_PASSWORD", "admin123")
