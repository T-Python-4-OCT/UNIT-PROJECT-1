# KickOff Tickets

An interactive command-line app for booking football match tickets in the **Roshn Saudi League 2026-2027**.
Teams, results and fixtures come from the official SAFF page (data typed by hand, no web scraping)
([Roshn Saudi League fixtures](https://www.saff.com.sa/championship.php?id=415&type=all#fixtures)), saved as a snapshot of the results up to **24 Oct 2026** (round 11), with the round 12 fixtures (29-31 Oct) as upcoming matches.
The league table is calculated by the program from those results.

## Overview

A fan browses matches, picks seats inside a drawn stadium, pays, and gets an e-ticket.

The main menu has six options: **Book tickets**, **League standings**, **Matches**, **My bookings**,
**My cart and checkout** and **Team profiles and logos** (and `0` to exit).

**Book tickets** shows a numbered table of the upcoming matches. Type a match number and the stadium opens
(north stand on top, the pitch in the middle, south stand below) with every seat drawn in a color:

| Color | Meaning |
|-------|---------|
| Green | Seat is free |
| Yellow | Seat is held for 5 minutes (someone put it in the cart). Nobody else can take it until the time runs out |
| Red | Seat is booked and paid. Everyone who opens the match sees it red |

## User stories

**As a fan I can:**

* Browse upcoming matches, or filter by team or date, and see finished results.
* View match details: teams and their table positions, date and stadium.
* Type a match number from the booking table and open the stadium drawing.
* Add seats by typing seat codes (type a seat again to remove it). A chosen seat is held for 5 minutes.
* List my cart, remove a seat, or empty it.
* Check out: name, phone, optional coupon, payment method (card, Apple Pay, STC Pay: simulation only).
* Get a receipt on screen and an e-ticket file in the `tickets/` folder.
* Check the status of my tickets (confirmed / cancelled, match upcoming / finished), cancel a booking, and read my e-ticket files.
* View the league table: full table, top 5, or relegation zone.
* Open a team profile and its logo in my browser.

## Usage

```bash
python -m venv venv
venv\Scripts\Activate.ps1          # Windows PowerShell   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python main.py
```

Everything is menu driven: type the number of an option and press Enter. `0` always goes back.
Make the terminal window wide enough (about 95 columns) so the stadium is drawn correctly.

Seat map commands:

| You type | What happens |
|----------|--------------|
| `a3` | Seat A3 turns yellow (held for 5 minutes and added to the cart). Type `a3` again to remove it |
| `a3 a4 b1` | Several seats at once |
| `clear` | Release all your seats of this match |
| `done` | Leave the stadium (the program offers to go to checkout) |

Seat prices (sample values): the rows closest to the pitch are the most expensive.
Rows C and D are **VIP 250 SAR**, rows B and E are **Standard 60 SAR**, rows A and F are **Family 30 SAR**.
You can hold at most 5 seats per match.
Coupon codes: `KICKOFF10` (10% off), `WELCOME5` (5% off).

## Points and the league table

Points = 3 x wins + draws. The table is sorted by points, then goal difference, then goals scored.
The table includes all results up to 24 Oct 2026 (a snapshot, it does not change while the program runs).

## Project structure

```
UNIT-PROJECT-1/
├── main.py                 # starts the program
├── requirements.txt
├── .gitignore              # venv, cache, runtime data and tickets
├── data/seed/              # starting data (teams, matches, demo bookings)
└── kickoff/                # the package
    ├── models.py           # Team, Match, Booking, Cart
    ├── payment.py          # PaymentMethod (abstract), CardPayment, ApplePay, StcPay
    ├── pricing.py          # rows, categories, prices, coupons
    ├── storage.py          # read/write JSON, tickets, activity log
    ├── standings.py        # sorting the table
    ├── booking.py          # cart, checkout, cancel
    ├── holds.py            # temporary 5-minute seat holds (yellow seats)
    ├── seatmap.py          # the stadium drawing with colored seats
    ├── ui.py               # input helpers and rich tables
    ├── decorators.py       # @safe_action and @log_action
    ├── errors.py           # custom exceptions
    ├── session.py          # shared state while the program runs
    └── fan_menu.py         # all menu options
```

Concepts used (Unit 1): CLI, Git and GitHub, variables with type hints, data types and casting, operators,
if/elif/else, loops with `range`, functions (parameters, return values, scope with `global`), lists, tuples,
dictionaries and sets, modules and packages, file and directory operations, recursion (`ask_int`), `lambda`,
`try / except / else / finally`, decorators, classes (encapsulation, inheritance, abstract class), and a virtual
environment with pip and `requirements.txt`.

## Notes

* Payments are a simulation. Never type a real card number. Only the last 4 digits are kept in the booking.
* Prices, seat categories and the 60-seat sample stand are made up for this project. Teams, results and fixtures come from SAFF (24 Oct 2026); the table is calculated from the results.
* Runtime files (`data/*.json`, `tickets/`) are created when the program runs and are ignored by Git.
* Logos are not drawn in the terminal. The team profile can open the logo in your browser.