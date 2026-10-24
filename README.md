# 🎬 VOX Cinema Booking (CLI)

## Overview
**VOX Cinema Booking** is an interactive command-line program that lets customers book cinema tickets
in **5 VOX cinemas in Riyadh**. The customer chooses a cinema, a movie, an experience
(**Standard, IMAX or Suites**), a day and a show time, then picks seats from a **colored seat map**
drawn inside the terminal.

Every booking gets an **invoice number** and is saved in a JSON file, so the customer can close the
program, open it again, and find, change or cancel the booking using their **name or invoice number**.

The goal of the project is to practice everything from Unit 1: CLI, Git & GitHub, variables and types,
flow control, functions, data structures, modules & packages, files, recursion, lambda, exceptions,
decorators, OOP, and virtual environments with pip.

## Features
- 🏢 **5 cinemas**: VOX Riyadh Park, VOX Sahara Mall, VOX Al Qasr Mall, VOX Atyaf Mall, VOX The Sport.
- 🎞️ Each cinema shows **10 real movies**: new 2026 releases (Avengers: Doomsday, Spider-Man: Brand New Day, Toy Story 5...) and classics (The Shawshank Redemption, Interstellar, The Godfather...).
- 📅 Showtimes every day from **21 to 31 October 2026**, 4 showtimes a day.
- 🎟️ **3 experiences** with different seat maps and prices:

  | Experience | Seats | Layout | Price |
  |---|---|---|---|
  | Standard | 48 | Rows A-F, seats 1-8 | A-D Regular **40 SAR**, E-F Premium **60 SAR** |
  | IMAX | 60 | Rows A-F, seats 1-10 | **80 SAR** |
  | Suites | 32 | Rows A-D, seats 1-8 in couple pairs | **150 SAR** |

- 🟩🟥 **Seat map** with the screen and separate colored squares: green = free, red = booked, yellow = your choice.
- 👥 Book **several seats** in one booking (for friends), up to 6.
- 🧾 **Invoice number + ticket**, with an option to save the ticket as a `.txt` file.
- 🔎 **My bookings**: search by name or invoice number, view, **change seats**, **cancel**, export.
- 🤖 **Recommendations** based on your booking history (your favourite genre).
- 📊 **Statistics**: tickets, revenue, most popular movie, charts per movie / experience / cinema.
- 🌤️ **Real weather forecast** for the show day (Open-Meteo API) with a smart tip.
- 🛡️ **Input validation everywhere**: wrong numbers, wrong names, booked seats, invalid seats.
- 💾 Data is saved in `data/bookings.json` and loaded again on the next run.

## User Stories
As a **customer** I should be able to:
- Enter my name so the booking is saved under my name.
- Choose one of the 5 cinemas.
- Browse the 10 movies of the cinema (year and genre).
- Choose an experience: Standard, IMAX or Suites, and see the prices.
- Choose a day (21-31 October) and a showtime.
- See the seat map with the screen, and know which seats are free or booked.
- Choose a seat, get an error if it is booked, and choose another one.
- Add more seats for my friends.
- See a summary with the price of every seat and the total before confirming.
- Get an invoice number and a ticket after confirming.
- Save my ticket as a text file.
- See the weather on the show day.
- Find my bookings later by my name or invoice number.
- Change the seats of my booking and see how much more I pay or get back.
- Cancel my booking.
- Get movie recommendations based on what I booked before.
- See cinema statistics.

## Installation
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd vox-cinema-booking

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 3. Install the packages
pip install -r requirements.txt

# 4. Run the program
python main.py
```

## Usage
Type the **number** of the option and press **Enter**.

| Main menu option | What it does |
|---|---|
| `1` Book a ticket | Name → cinema → movie → experience → showtime → seats → confirm |
| `2` My bookings | Type your **full name** or **invoice number**, then view / change seats / cancel / save ticket |
| `3` Recommendations for me | Type your name to get movies from your favourite genre |
| `4` Cinema statistics | Tickets, revenue and charts |
| `5` How to use | Short help screen |
| `6` Exit | Close the program |

**Choosing seats:** type the row letter and the seat number, for example `B5`
(`b5` and `B-5` also work). Type `Q` to stop choosing.
After each seat you are asked `Do you want to book another seat? (yes/no)`.

Example:
```
Enter a seat (example: B5) or Q to stop: A3
✘ Seat A3 is already booked (red). Please choose a green seat.
Enter a seat (example: B5) or Q to stop: D1
✔ Seat D1 (Regular, 40 SAR) added.
Do you want to book another seat (for a friend)? (yes/no): no
```

## Project Structure
```
vox-cinema-booking/
├── main.py                        # Main menu - starts the program
├── cinema/                        # Main package
│   ├── __init__.py
│   ├── config/                    # Static data
│   │   ├── __init__.py
│   │   ├── settings.py            # App name, booking rules, file paths, city
│   │   ├── movies.py              # 15 real movies (2026 + classics)
│   │   └── branches.py            # The 5 cinemas and their 10 movies
│   ├── models/                    # Classes (OOP)
│   │   ├── __init__.py
│   │   ├── hall.py                # Hall base class
│   │   ├── hall_types.py          # StandardHall, ImaxHall, SuitesHall (inheritance)
│   │   └── booking.py             # Booking class
│   ├── storage/                   # Files
│   │   ├── __init__.py
│   │   ├── bookings_file.py       # Load / save the JSON file
│   │   ├── search.py              # Search by name / invoice, booked seats
│   │   └── tickets.py             # Export a ticket as a .txt file
│   ├── services/                  # Smart features
│   │   ├── __init__.py
│   │   ├── weather.py             # Weather API (requests)
│   │   ├── recommendations.py     # Movies from your favourite genre
│   │   └── statistics.py          # Tickets, revenue, most popular movie
│   ├── ui/                        # Terminal helpers
│   │   ├── __init__.py
│   │   ├── display.py             # Titles and colored messages
│   │   ├── inputs.py              # Safe input + validation (recursion)
│   │   ├── decorators.py          # @pause_after decorator
│   │   └── seat_map.py            # Draws the screen and the colored seats
│   └── screens/                   # What the user sees
│       ├── __init__.py
│       ├── choosers.py            # Choose cinema, movie, experience, showtime
│       ├── seat_picker.py         # Choose seats from the map
│       ├── booking_screen.py      # "Book a ticket" (7 steps)
│       ├── my_bookings_screen.py  # View / change seats / cancel / export
│       ├── insights_screen.py     # Recommendations and statistics
│       └── help_screen.py         # How to use
├── data/                          # Created automatically: bookings.json
├── tickets/                       # Created automatically: ticket_XXXXX.txt
├── requirements.txt
├── README.md
└── .gitignore
```

## Project Requirements Checklist
| Requirement | How it is done |
|---|---|
| Interactive on CLI | Numbered menus, step-by-step booking, colored seat map |
| Python used accurately | Clear names, small functions, input validation, no crashes on wrong input |
| Organized into modules & packages | `cinema/` package with 6 sub-packages: config, models, storage, services, ui, screens |
| Git & GitHub | Commits for every development stage |
| Full CRUD + search | Book (create), view, change seats (update), cancel (delete), search by name / invoice |
| Save & load data | `data/bookings.json`, tickets exported to `tickets/*.txt` |
| Creativity | Real weather API, recommendations, statistics with text charts |
| `requirements.txt` | Generated with `pip freeze > requirements.txt` |

## Unit 1 Concepts Used
| Concept | Where |
|---|---|
| Variables, type hints, casting, f-strings | All files (`int(text)`, `-> list[str]`) |
| if / elif / else, for, while, range | `ui/seat_map.py`, `ui/inputs.py`, `screens/seat_picker.py` |
| Functions, parameters, return values | Every module |
| Lists, tuples, dictionaries, sets | `config/` (dict, tuple), `storage/search.py` (set of booked seats) |
| Modules & packages, imports | `cinema/` package with 6 sub-packages |
| File & directory operations | `storage/` (JSON, `.txt` tickets, `os.makedirs`) |
| Recursion | `ui/inputs.py` → `ask_yes_no()` |
| Lambda | `services/statistics.py`, `services/recommendations.py`, `screens/my_bookings_screen.py` |
| Exceptions (try / except / else / finally) | `storage/bookings_file.py`, `services/weather.py`, `main.py` |
| Decorators | `ui/decorators.py` → `@pause_after` |
| OOP: classes, methods, inheritance | `models/hall.py` → `models/hall_types.py`; `models/booking.py` |
| venv & pip | `colorama`, `requests`, `requirements.txt` |

## Built With
- Python 3.10+
- [colorama](https://pypi.org/project/colorama/) – colors in the terminal
- [requests](https://pypi.org/project/requests/) – weather from the [Open-Meteo API](https://open-meteo.com/)
