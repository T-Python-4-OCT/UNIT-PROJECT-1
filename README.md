# SkyRoute ✈️ - Travel Agency CLI

An interactive command-line travel agency built with Python. Customers can explore
28 destinations with **live weather**, tell the app their **budget** and get a day-by-day
trip plan, then book, pay and receive a receipt, with **real confirmation emails** at each
step. The manager runs the agency: destinations, customers, bookings and revenue reports.

## Goal

Planning a trip usually means jumping between many websites. SkyRoute puts the whole
journey in one place: *where can I go with my money?* -> *what will the weather be?* ->
*book and pay* -> *receipt by email*, while giving the agency owner the tools to manage it.
It was built to practice Python fundamentals: functions, loops, validation, modules,
file storage, an external API, email (SMTP), testing and Git.

> **Note:** all prices are rough estimates in SAR (round-trip flight from Riyadh +
> daily costs per person). They are for learning purposes, not for real booking.

## Features & User Stories

**As a customer I can:**
- Register with my username, full name, **email and mobile number**, and I am told my
  **customer ID**. A welcome email is sent to the address I typed.
- Log in and see a **welcome message** with my customer ID and what needs my attention
  (unpaid bookings, my next trip).
- Browse all destinations (country with its **flag**, most famous city, trip type with an emoji, flight and hotel prices).
  Trips the manager has suspended are shown with a line through them.
- View destination details: highlights, best season, daily costs.
- Search destinations **by country, by city or by type** (city / beach / culture /
  adventure). Small spelling mistakes are fixed, so `turky` still finds Turkey.
  I can pick a result to see its **city details and live weather**.
- See **live weather and a forecast** for the destination city (real data from the
  Open-Meteo API; if there is no internet the app shows a warning and keeps working).
  The same information appears in the details, search and budget-plan screens.
- Enter my budget, number of travelers and travel style (economy / standard / luxury) and
  the **number of days** (7 is suggested, but I choose what suits me, from 2 to 30). I get
  matching trips with the city details (type, best season, highlights); when I pick one I
  see the city information, its weather, a day-by-day itinerary and a cost breakdown.
- Get a **10% group discount** when we are exactly two travelers (the app announces it when it asks for the number of travelers and shows it as a line in the price).
- Book a trip with a travel date (suspended trips cannot be booked). Before payment the app asks
  *"Do you have a discount code? Type it, or type no"*; a valid occasion code (for example `EID20`) takes
  **20% off**, then the customer goes straight to payment.
- Pay by card (**name on card, card number of 8-16 digits and CVV**) or Apple Pay and get a payment reference.
- **Get an email** on my registered address when I register, book, pay or cancel.
- View my bookings and their status (pending / confirmed / completed / cancelled).
- Cancel a booking. Paid bookings show the refund amount and the message
  *"Your money will be refunded within 24 hours to 4 business days."* (also in the email).
- Get a receipt for paid bookings.
- Choose the **trip type** and **trip length** I want and get recommendations: the city,
  its type, its weather and a day-by-day plan.

**As a manager I can:**
- See a welcome message and a dashboard: revenue, bookings by status, top destinations,
  customers count.
- See **who booked**: the booking list shows each customer's name, username, ID, email
  and mobile number.
- List all customers (with their booking numbers and the money they paid).
- **Delete a customer.** Their active bookings are cancelled and paid ones refunded, they
  are told by email, and completed or cancelled bookings stay in the records as history
  (shown as "Deleted customer #id"). Managers cannot be deleted.
- Update booking status (completed, cancelled with refund...). The customer is emailed
  when a booking is cancelled or completed.
- Add, edit and delete destinations.
- Manage **discount codes for annual occasions** (Eid, end-of-year holiday...): add a code with its
  occasion (20% by default), switch it on or off, or delete it. `EID20` and `YEAREND10` are ready from
  the first run. Bookings that already used a code keep their discount.
- **Suspend a trip until further notice** (and resume it later). A suspended trip is
  struck through in every list, cannot be booked and is not recommended or planned.
  Existing bookings are not changed; the manager can still cancel them.

## Libraries

| Library | Why |
|---|---|
| [rich](https://pypi.org/project/rich/) | colors, tables, panels, red error messages, prompts |
| [pyfiglet](https://pypi.org/project/pyfiglet/) | Text Art banner |

Everything else is the Python standard library (json, hashlib, dataclasses, unittest,
`urllib` for the weather API, `smtplib` for email, ...). The weather comes from the free
[Open-Meteo](https://open-meteo.com/) API, which needs no API key.

## Setup & Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate           # macOS / Linux
python -m pip install -r requirements.txt
python main.py
```

`requirements.txt` lists the minimum versions (the code was tested with `rich` 13.4.2).
To lock the exact versions installed on your machine, run
`python -m pip freeze > requirements.txt`.

**Default manager account:** `admin` / `admin123`
Customers create their own account from the welcome menu.
Demo card for payments: any name, any card number of 8 to 16 digits, any 3-digit CVV.
Card details are checked and never saved. Demo discount codes: `EID20`, `YEAREND10`.

## Email setup (optional)

Emails are sent with Python's built-in `smtplib`, so no extra library is needed.

1. Copy `.env.example` to a new file named `.env` (next to `main.py`).
2. Fill in your own mail account. For Gmail, turn on 2-Step Verification and create an
   **App password** at <https://myaccount.google.com/apppasswords>; the normal Gmail
   password is rejected.
3. Check it works: `python main.py --test-email your_address@gmail.com`. Open the Gmail app on your phone:
   the test email should arrive in a few seconds.
4. Run the program. After a registration, booking or payment you will see
   `✉ An email was sent to ...`; the payment email is the receipt.

Without a `.env` file everything still works: each email is saved as a readable text file in
`data/outbox/` and the screen says so. If the mail server cannot be reached the booking is
still made and the screen shows the reason. The `.env` file holds a password, so it is listed
in `.gitignore` and must never be uploaded to GitHub.

## Usage

1. Welcome menu: type `1` to login, `2` to register, `0` to exit.
2. Customer menu - type the number of the action:

| # | Action |
|---|---|
| 1 | Browse destinations |
| 2 | View destination details + live weather (type the ID) |
| 3 | Search destinations: choose *country*, *city* or *type*, then pick a result for its details and weather |
| 4 | Plan a trip by budget (days default to 7, any length allowed; two travelers get 10% off) |
| 5 | Book a trip (date, discount code, then straight to payment) |
| 6 | My bookings |
| 7 | Pay for a booking (card: name, number, CVV / Apple Pay) |
| 8 | Cancel a booking |
| 9 | View receipt |
| 10 | Recommendations: pick a trip type (or `any`) and the number of days |
| 0 | Logout |

3. Manager menu:

| # | Action |
|---|---|
| 1 | Dashboard and revenue report |
| 2 | List all bookings (with customer details) |
| 3 | Update booking status |
| 4 | List customers |
| 5 | Delete a customer |
| 6 | List destinations |
| 7 | Add destination |
| 8 | Edit destination |
| 9 | Delete destination |
| 10 | Suspend / resume a trip |
| 11 | Discount codes (list, add, on/off, delete) |
| 0 | Logout |

**Example: plan and book a trip as a customer**
- type `2` at the welcome menu to register (username, full name, email, mobile number, password), or `1` to log in.
- type `4` (plan a trip by budget), then enter a budget such as `20000`; press Enter to accept 7 days, type `2` for two travelers (10% off), and pick a trip type.
- type the number of a result to see its city details, live weather, day-by-day plan and cost breakdown, then `y` to book it.
- enter the travel date as `2026-12-25`, and a discount code such as `EID20` (or `no`).
- type `y` to pay now, choose `card`, and enter any name, a card number of 8-16 digits and a 3-digit CVV.
- type `9` to see the receipt; a confirmation email is sent to the address you registered with.

**Example: search**
- type `3`, choose `city`, and type `turky` or `Dubai`; pick a result ID to see its details and weather.

**Going back:** at any question type `b` (or `back`) to cancel and return to the menu; on ID questions `0` also works. Nothing is saved when you go back.

Colors: **green** = success, **red** = error, **yellow** = warning, **cyan** = info.

## Project Structure

```
skyroute/
├── main.py                  entry point: welcome menu, login, register
├── .env.example             template for the email settings (copy to .env)
├── agency/
│   ├── config.py            paths and constants (default trip length, refund notice)
│   ├── errors.py            ServiceError (user-facing errors)
│   ├── flags.py             country flags (emoji from the ISO code)
│   ├── seed.py              creates the first data files
│   ├── countries_data.py    the 28 destinations
│   ├── models/              dataclasses: User, Country, Booking
│   ├── storage/json_db.py   read/write JSON files safely
│   ├── services/            business logic (no printing here)
│   │   ├── auth.py  users.py (customers, deletion)  countries.py  planner.py  promos.py (discount codes)
│   │   ├── bookings.py  reports.py (dashboard + welcome notes)  recommendations.py
│   │   └── weather.py (Open-Meteo)  notifications.py (emails)
│   ├── ui/                  everything the user sees
│   │   ├── console.py       colors, banner, input helpers
│   │   ├── views.py         tables and panels
│   │   └── customer_menu.py  manager_menu.py
│   └── utils/               security.py, validators.py, env_file.py (.env reader)
└── tests/                   test_services.py, test_ui_smoke.py (run them to see the count)
```

Layers: **models** hold data, **services** hold logic, **ui** handles display and input.

## Tests

```powershell
python -m unittest discover -s tests -v
```
The tests cover the business rules (planning math, booking, card validation, refunds,
status rules, group and occasion discounts, suspended trips, search with spelling fixes, recommendations by type,
customers and their deletion, reports), the weather parsing (with a fake API, so they run
offline), the emails (with a tiny local mail server, so the real SMTP conversation is tested
without sending anything) and the menus (with fake prompts). The tests never use your `.env`.

**Improved from user feedback:**
- Round 1: users asked for a way to go back from any question (now `b`), and the card
  number is now visible while typing because the hidden input confused users.
- Round 2: bank transfer was removed and card payment now asks for name, number and CVV;
  customers see how long a refund takes; recommendations ask for the trip type first and
  show weather and a plan; search offers country / city / type and fixes spelling;
  budget plans show city details; a welcome message appears after login; the manager can
  suspend trips until further notice.
- Round 3: registration asks for a mobile number and shows the customer ID; customers get
  real emails; the manager can see who booked and delete customers; trips default to
  7 days (any length allowed); search and budget plans also show the city information and
  live weather.
- Round 4: the days question says "choose what suits you"; two travelers get 10% off; the manager
  creates discount codes for Eid and the end-of-year holiday (20%); the app asks for a code before
  payment and then goes straight to it; card numbers accept 8 to 16 digits; `--test-email` checks
  that the mail arrives on a phone.

## Git workflow

Work is committed in stages, for example:
```
feat: project structure, storage and seed data
feat: authentication with roles
feat: browse, details and search destinations
feat: budget-based trip planner
feat: booking and cancellation
feat: payment, receipt and booking status
feat: manager dashboard and reports
feat: recommendations and live weather
feat: customer emails, customer management and 7-day default
feat: group discount and occasion discount codes
docs: readme and requirements
```
`.gitignore` excludes `.venv/`, `__pycache__/`, the `data/` folder (accounts, bookings and
saved emails are created at runtime) and the `.env` file (it contains the mail password).

## Security notes
- Passwords are stored as salted PBKDF2-SHA256 hashes, never as plain text.
- Card details (name, number, CVV) are only checked (number: 8-16 digits) and never saved or
  emailed.
- The email password lives only in your `.env` file or environment variables, which are
  never uploaded; the program never prints it.
- Customer names and emails are checked so they cannot inject extra lines into an email.
- The `data/` folder is in `.gitignore` and is recreated automatically.
