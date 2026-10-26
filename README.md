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
- 📅 Showtimes for the **next 7 calendar days** (past start times are hidden), 4 showtimes per day.
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
- 🌤️ **Real food and drinks forecast** for the show day (optional popcorn, drinks and snacks) with a smart tip.
- 🛡️ **Input validation everywhere**: wrong numbers, wrong names, booked seats, invalid seats.
- 💾 Data is saved in `data/bookings.json` and loaded again on the next run.

## User Stories
As a **customer** I should be able to:
- Enter my name so the booking is saved under my name.
- Choose one of the 5 cinemas.
- Browse the 10 movies of the cinema (year and genre).
- Choose an experience: Standard, IMAX or Suites, and see the prices.
- Choose an available day in the next 7 days and a showtime.
- See the seat map with the screen, and know which seats are free or booked.
- Choose a seat, get an error if it is booked, and choose another one.
- Add more seats for my friends.
- See a summary with the price of every seat and the total before confirming.
- Get an invoice number and a ticket after confirming.
- Save my ticket as a text file.
- See the food and drinks on the show day.
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

## Complete Booking Walkthrough — All 7 CLI Steps

Below is an **illustrative full booking session**, showing what a customer sees at every stage. The examples follow the actual program flow, but the selected date, reserved seats, and invoice number can change when you run it. Each step is displayed on a separate terminal screen (the program clears the previous screen).

### Main menu — Start booking

```text
============================================================
                      VOX CINEMAS
============================================================
  1. Book a ticket
  2. My bookings (view / change seats / cancel)
  3. Recommendations for me
  4. Cinema statistics
  5. How to use
  6. Exit

Choose a number: 1
```

### Step 1/7 — Your name

```text
============================================================
                 Step 1/7 - Your name
============================================================
Enter your full name: Ahmed Ali
```

### Step 2/7 — Choose a cinema

```text
============================================================
               Step 2/7 - Choose a cinema
============================================================
  1. VOX Riyadh Park
  2. VOX Sahara Mall
  3. VOX Al Qasr Mall
  4. VOX Atyaf Mall
  5. VOX The Sport

Choose a cinema: 1
```

### Step 3/7 — Choose a movie

```text
============================================================
             Step 3/7 - Movies at VOX Riyadh Park
============================================================
  1. Avengers: Doomsday             2026   Action
  2. Spider-Man: Brand New Day      2026   Action
  3. The Super Mario Galaxy Movie  2026   Animation
  4. Toy Story 5                   2026   Animation
  5. Project Hail Mary             2026   Sci-Fi
  6. The Odyssey                   2026   Adventure
  7. Supergirl                     2026   Action
  8. The Shawshank Redemption      1994   Drama
  9. Interstellar                  2014   Sci-Fi
 10. The Dark Knight               2008   Action

Choose a movie: 9
```

### Step 4/7 — Choose your experience

```text
============================================================
           Step 4/7 - Choose your experience
============================================================
  1. Standard  48 seats - Classic cinema experience
                Rows A-D Regular: 40 SAR | Rows E-F Premium: 60 SAR
  2. IMAX      60 seats - Giant screen and powerful sound
                80 SAR per seat
  3. Suites    32 seats - Luxury recliner seats in couple pairs
                150 SAR per seat

Choose an experience: 1
```

### Step 5/7 — Choose your showtime

```text
============================================================
             Step 5/7 - Choose your showtime
============================================================
  1. Mon 26 Oct 2026
  2. Tue 27 Oct 2026
  3. Wed 28 Oct 2026
  4. Thu 29 Oct 2026
  5. Fri 30 Oct 2026
  6. Sat 31 Oct 2026
  7. Sun 01 Nov 2026

Choose a day: 2

  1. 13:30
  2. 16:00
  3. 19:15
  4. 22:30

Choose a showtime: 3
```

*The dates above are just an example. The application displays the next seven calendar days and hides showtimes that have already started.*

### Step 6/7 — Select your seats

```text
============================================================
 Step 6/7 - Interstellar - Standard - Tue 27 Oct 2026 19:15
============================================================

                     S C R E E N
                ---------------------
                  1  2  3  4  5  6  7  8
             A    🟩 🟩 🟥 🟩 🟩 🟩 🟥 🟩
             B    🟩 🟩 🟩 🟩 🟥 🟩 🟩 🟩
             C    🟩 🟩 🟩 🟩 🟩 🟩 🟩 🟩
             D    🟩 🟩 🟩 🟩 🟩 🟩 🟩 🟩
                 -- PREMIUM SEATS --
             E    🟩 🟩 🟩 🟩 🟩 🟩 🟩 🟩
             F    🟩 🟩 🟩 🟩 🟩 🟩 🟩 🟩

🟩 Available    🟥 Booked    🟨 Your choice
Prices -> Rows A-D Regular: 40 SAR | Rows E-F Premium: 60 SAR

Enter a seat (example: B5) or Q to stop: D1
✔ Seat D1 (Regular, 40 SAR) added.
Do you want to book another seat (for a friend)? (yes/no): no
```

*The real seat map is drawn using colored terminal backgrounds (green/red/yellow), rather than emoji squares; this simplified illustration makes it easier to read in GitHub.*

### Step 7/7 — Booking summary and confirmation

```text
============================================================
              Step 7/7 - Food, drinks and booking summary
============================================================
Customer      : Ahmed Ali
Cinema        : VOX Riyadh Park
Movie         : Interstellar (2014)
Experience    : Standard
Your showtime : Tue 27 Oct 2026 at 19:15
----------------------------------------
  Seat D1   Regular       40 SAR
----------------------------------------
  TOTAL (1 seats)          40 SAR

Confirm this booking? (yes/no): yes
✔ Booking confirmed! Keep your invoice number: [generated number]
```

After confirmation, the program prints the **ticket** and the **food and drinks forecast (if available)**, then asks whether to save the ticket as a `.txt` file. Booking and invoice data are saved in JSON so they can be found later from **My bookings**.

## Project Structure
```
vox-cinema-booking/
├── main.py                        # Main menu - starts the program
├── cinema/                        # Main package
│   ├── __init__.py
│   ├── config/                    # Static data
│   │   ├── __init__.py
│   │   ├── settings.py            # App name, booking rules, file paths
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
│       ├── snacks_screen.py       # Optional food and drinks
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

## Built With
- Python 3.10+
- [colorama](https://pypi.org/project/colorama/) – colors in the terminal




## Optional Food & Drinks (Step 7/7)

Before confirming the booking, you may add one item from each category:

- **Popcorn:** Small 10 SAR, Medium 15 SAR, Large 20 SAR
- **Drinks:** Small 8 SAR, Medium 12 SAR, Large 16 SAR
- **Snacks:** Chocolate 7 SAR, Hot dog 18 SAR, Nachos 16 SAR, Candy 6 SAR, Nuts 9 SAR

Choose a quantity from 1 up to your booked seats. Press **Enter** to use one item per seat. You can skip all extras. The booking summary and saved ticket show ticket costs, food/drinks, and the grand total. Existing bookings without food/drinks still load correctly.

```text
Step 7/7 - Food, drinks and booking summary
Add popcorn, a drink or a snack to your booking? (yes/no): yes
  1. Popcorn
  2. Drink
  3. Snack
  4. Done adding items
Choose a number: 1
  1. Small - 10 SAR
  2. Medium - 15 SAR
  3. Large - 20 SAR
Choose a number: 2
Quantity (1-3, Enter = 3 seats): 2
Added: 2 x Popcorn Medium = 30 SAR
Add something from another category? (yes/no): no

Your booking summary:
  Tickets (3 seats)      120 SAR
  Food & drinks:
  Popcorn Medium         2 x 15 = 30 SAR
  Extras total            30 SAR
  GRAND TOTAL            150 SAR
Confirm this booking? (yes/no): yes
```

### Dependencies

Only `colorama` is required from pip. In your virtual environment, uninstall the unused `requests` package if needed, then run `python -m pip freeze > requirements.txt`.
