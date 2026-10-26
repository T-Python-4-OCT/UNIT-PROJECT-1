# UNIT-PROJECT-1
# Majlis Table - Restaurant Reservation System

## Overview
Majlis Table is a command-line application that manages table reservations for a restaurant. It has two types of users: the **customer**, who books tables, and the **manager**, who controls the tables and all bookings.

**Goal of the project:** booking by phone or on paper leads to double bookings, forgotten reservations and no clear picture of which tables are free. This program solves that: it never books the same table twice at the same time, respects the opening hours, and keeps all data saved between runs.

Everything is done by choosing **numbers** from colored, boxed menus, so nothing has to be memorized.

Rules of the restaurant (editable in `config.py`):
* Open from 12:00 to 23:00.
* Every booking holds a table for 90 minutes.
* Bookings can be made up to 7 days ahead, in 30-minute steps.

## Main Features
* Numbered, colored and boxed menus built with the `rich` library (green = available, red = not available, yellow = in progress).
* Guided booking: number of guests, then day, time and table. Taken times and tables are shown in red and cannot be chosen.
* No double booking: two bookings can never overlap on the same table.
* Automatic validation (past dates, closed hours, wrong phone number, too many guests).
* Booking receipt, printed after booking and available at any time.
* Time left for every booking (`starts in 1h 30m`, `45m left`, `finished`).
* Search for tables by location or by minimum seats.
* Live table status (Free now / Occupied now).
* Manager tools: add/remove tables, view bookings by day, cancel any booking, statistics.
* Password-protected manager area: the manager creates his own password at the first login, and it is stored **hashed** (never as plain text). 3 login attempts.
* All data is saved in JSON files, so nothing is lost when the program closes.
* Unit tests for the booking rules and the password.

## User Stories

### As a customer I should be able to do the following:
* Browse the tables of the restaurant (seats, location and current status).
* Search for tables by location or by minimum number of seats.
* Book a table by choosing the number of guests, the day, the time and the table.
* See which times and tables are available before choosing.
* List my upcoming bookings and see how much time is left for each.
* Get a receipt of my booking.
* Cancel one of my bookings.
* Get clear messages if I enter something wrong.

### As a manager I should be able to do the following:
* Create my own password the first time I enter, then log in with it.
* Browse all the tables.
* Add a new table (seats and location).
* Remove a table (not allowed if it has upcoming bookings).
* List all upcoming bookings with the customer's name, phone and time left.
* List the bookings of a specific day.
* Cancel any booking.
* View statistics (total, confirmed, cancelled and upcoming bookings, busiest table).

## What You Need
* Python 3.8 or newer.
* The `rich` package (installed from PyPI, see below).
* An internet connection to install the package.

## Installation and Running
```bash
# 1) Go to the project folder
cd majlis_table

# 2) Create a virtual environment
python -m venv venv

# 3) Activate it
#    Windows (PowerShell):  .\venv\Scripts\Activate.ps1
#    Windows (Git Bash):    source venv/Scripts/activate
#    Mac / Linux:           source venv/bin/activate

# 4) Install the required package
pip install -r requirements.txt

# 5) Run the program
python main.py
```
On the first run the program creates a `data/` folder with the JSON files and six default tables.

If PowerShell refuses to activate the environment, run this once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

To turn the colors off, set the environment variable `NO_COLOR=1`.


## Usage
Everything is chosen by typing the **number** of an option and pressing Enter. Type `0` to go back.

### Main menu
* type in `1` to enter as a customer.
* type in `2` to enter as a manager.
* type in `0` to exit.

### As a customer
You are asked for your name and phone number first. Your phone number identifies your bookings, so you can only see and cancel your own.

* type in `1` to browse all the tables.
* type in `2` to search for tables (by location or by minimum seats).
* type in `3` to book a table (guests, then day, time and table).
* type in `4` to list your upcoming bookings and the time left for each.
* type in `5` to get the receipt of a booking.
* type in `6` to cancel a booking (you will be asked to confirm).
* type in `0` to go back to the main menu.

### As a manager
The first time you enter, the program asks you to create a password (at least 6 characters, typed twice). It is saved **hashed** in `data/admin.json`, so nobody can read it. After that you log in with it (3 attempts).

If you forget the password, delete `data/admin.json` and create a new one. Tables and bookings are not affected.

* type in `1` to view all the tables.
* type in `2` to add a table.
* type in `3` to remove a table.
* type in `4` to list all upcoming bookings.
* type in `5` to list the bookings of a specific day.
* type in `6` to cancel a booking.
* type in `7` to view the statistics.
* type in `0` to log out.

## Example Session

> The screens below are plain-text copies. In the real program the menus are colored.

### Example 1: a customer books a table

**Step 1 - Main menu:** type `1` to enter as a customer, then type your name (`Sara`) and your phone number (`0501234567`).
```
┌──────────── Main Menu ─────────────┐
│ 1. Customer                        │
│ 2. Manager                         │
│ 0. Exit                            │
└────────────────────────────────────┘
Your choice: 1
```

**Step 2 - Customer menu:** type `3` to book a table, then type the number of guests (`4`).
```
┌─────── Customer Menu - Sara ───────┐
│ 1. Browse tables                   │
│ 2. Search tables                   │
│ 3. Book a table                    │
│ 4. My bookings                     │
│ 5. Get a receipt                   │
│ 6. Cancel a booking                │
│ 0. Back to main menu               │
└────────────────────────────────────┘
Your choice: 3
```

**Step 3 - Choose a date:** type `2` for tomorrow.
```
┌────────── Choose a date ───────────┐
│ 1. Mon 26 Oct 2026 (today)         │
│ 2. Tue 27 Oct 2026 (tomorrow)      │
│ 3. Wed 28 Oct 2026                 │
│ 4. Thu 29 Oct 2026                 │
│ 5. Fri 30 Oct 2026                 │
│ 6. Sat 31 Oct 2026                 │
│ 7. Sun 01 Nov 2026                 │
│ 0. Cancel                          │
└────────────────────────────────────┘
Your choice: 2
```

**Step 4 - Choose a time:** green times have free tables, red times are full and cannot be chosen. Type `16` for 19:30.
```
┌────────── Choose a time ───────────┐
│ 1. 12:00   (4 table(s) free)       │
│ 2. 12:30   (4 table(s) free)       │
│ 3. 13:00   (3 table(s) free)       │
│ ...                                │
│ 8. 15:30   (full)                  │
│ ...                                │
│ 15. 19:00   (2 table(s) free)      │
│ 16. 19:30   (3 table(s) free)      │
│ ...                                │
│ 0. Cancel                          │
└────────────────────────────────────┘
■ available   ■ not available      (green = free, red = full)
Your choice: 16
```

**Step 5 - Choose a table:** only green tables can be chosen. Type `1` for table 3.
```
┌───────────── Choose a table ─────────────┐
│ 1. Table 3 - 4 seats, indoor             │
│ 2. Table 4 - 4 seats, outdoor   (booked) │
│ 3. Table 5 - 6 seats, family             │
│ 4. Table 6 - 8 seats, family             │
│ 0. Cancel                                │
└──────────────────────────────────────────┘
■ available   ■ not available      (green = free, red = booked)
Your choice: 1
```

**Step 6 - Receipt:** the booking is saved and the receipt is printed.
```
Booked successfully!
┌────── Majlis Table - Booking Receipt ──────┐
│ Reservation # : 1                          │
│ Name          : Sara                       │
│ Phone         : 0501234567                 │
│ Date & Time   : 2026-10-27 19:30           │
│ Duration      : 90 minutes                 │
│ Guests        : 4                          │
│ Table         : 3 (4 seats, indoor)        │
│ Status        : confirmed                  │
│                                            │
│ Thank you for choosing us!                 │
└────────────────────────────────────────────┘
```

**Step 7 - My bookings:** back in the customer menu, type `4` to see your bookings and the time left.
```
                          My bookings
┌────┬──────────────────┬────────┬───────┬─────────────────────┐
│ ID │ When             │ Guests │ Table │ Time                │
├────┼──────────────────┼────────┼───────┼─────────────────────┤
│ 1  │ 2026-10-27 19:30 │ 4      │ 3     │ starts in 1d 2h 15m │
└────┴──────────────────┴────────┴───────┴─────────────────────┘
```

**What happens with wrong input:**
```
Name cannot be empty.
Phone must be 9-15 digits (e.g. 0501234567).
Please type a number between 1 and 20.
That option is not available. Please choose a green one.
No table is big enough for that many guests.
```

### Example 2: browsing the tables
From the customer menu type `1`. A table is `Occupied now` while a booking is running on it.
```
                 Tables
┌────┬───────┬──────────┬──────────────┐
│ ID │ Seats │ Location │ Status       │
├────┼───────┼──────────┼──────────────┤
│ 1  │ 2     │ indoor   │ Free now     │
│ 2  │ 2     │ indoor   │ Free now     │
│ 3  │ 4     │ indoor   │ Occupied now │
│ 4  │ 4     │ outdoor  │ Free now     │
│ 5  │ 6     │ family   │ Free now     │
│ 6  │ 8     │ family   │ Free now     │
└────┴───────┴──────────┴──────────────┘
```

### Example 3: the manager enters for the first time
From the main menu type `2`. There is no password yet, so you create one (the text you type is hidden).
```
┌─────────── First-time setup ────────────┐
│ No manager password yet.                │
│ Create one now (at least 6 characters). │
└─────────────────────────────────────────┘
New password (empty = cancel):
Repeat the password:
Password saved. It is stored hashed, not as plain text.
```
Next time you only type the password:
```
Manager password:
```

### Example 4: manager menu - upcoming bookings
Type `4` in the manager menu.
```
                                   Upcoming bookings
┌────┬──────────────────┬────────┬───────┬─────────────────────┬──────────┬────────────┐
│ ID │ When             │ Guests │ Table │ Time                │ Customer │ Phone      │
├────┼──────────────────┼────────┼───────┼─────────────────────┼──────────┼────────────┤
│ 1  │ 2026-10-27 19:30 │ 4      │ 3     │ starts in 1d 2h 15m │ Sara     │ 0501234567 │
└────┴──────────────────┴────────┴───────┴─────────────────────┴──────────┴────────────┘
```

### Example 5: statistics
Type `7` in the manager menu.
```
┌──────────── Statistics ────────────┐
│ Total bookings : 6                 │
│ Confirmed      : 5                 │
│ Cancelled      : 1                 │
│ Upcoming       : 5                 │
│ Busiest table  : 3                 │
└────────────────────────────────────┘
```

## Colors
* Green: available (free table, free time, upcoming booking, success messages).
* Yellow: a booking that is running right now.
* Red: not available (full time, booked or occupied table, finished or cancelled booking) and error messages.

## How the Manager Password Is Stored
* The password itself is never saved, only its **hash**, which cannot be turned back into the password.
* It uses `PBKDF2` with `SHA-256` and a random **salt**, so two identical passwords give different hashes.
* At login the program hashes what you typed and compares it with the saved hash.
* The settings (minimum length, login attempts, iterations) are in `config.py`. Everything uses the Python standard library.

## Project Structure
```
majlis_table/
├── main.py              # entry point + main menu
├── config.py            # settings (hours, duration, locations, password settings)
├── models.py            # Table and Reservation classes
├── storage.py           # read/write JSON files
├── services/
│   ├── auth.py          # manager password (salted hash, verify)
│   ├── booking.py       # booking rules (availability, create, cancel, time left, stats)
│   └── tables.py        # add / remove / search tables
├── cli/
│   ├── ui.py            # rich: colors, boxes, tables, numbered menus, safe input
│   ├── common.py        # printing tables, bookings and receipts
│   ├── customer.py      # customer menu
│   └── manager.py       # manager menu
├── data/                # JSON files are created here on first run (not uploaded to GitHub)
├── requirements.txt     # packages used by the project
└── README.md
```

## Requirements
The project uses one external package from PyPI:

| Package | Used for |
|---|---|
| `rich` | colors, boxes and tables in the terminal |

Everything else comes from the Python standard library (`json`, `datetime`, `dataclasses`, `getpass`, `os`, `hashlib`, `hmac`, `secrets`, `unittest`).
The packages and their exact versions are listed in `requirements.txt`.