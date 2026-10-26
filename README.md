<div align="center">

# ✈️ SkyRoute

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&center=true&vCenter=true&width=520&lines=A+travel+agency+in+your+terminal+🌍;Plan+•+Book+•+Pay+•+Fly+🧳;Live+weather+☀️+Smart+receipt+🧾)](https://git.io/typing-svg)

![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/tests-179%20passed-brightgreen)
![API](https://img.shields.io/badge/weather-Open--Meteo-orange)
![Status](https://img.shields.io/badge/status-complete-success)

### 👨‍💻 Developed by **Mohammed Alnsafi**

</div>

## 📖 Overview
A command-line travel agency built with **Python**. Customers plan a trip by budget, book, pay, and get a **receipt** with the weather, a day-by-day plan and the local currency. The manager runs destinations, customers, bookings and discount codes. 🎓

## ✨ Features

| 👤 Customer | 🛠️ Manager |
|---|---|
| 🌍 Browse 28 destinations with flags | 📊 Dashboard and revenue report |
| 🔎 Search by country / city / type (fixes typos) | 👥 List and delete customers |
| ☀️ Live weather from an API | 🗺️ Add / edit / delete destinations |
| 💰 Trip plan based on your budget | ⏸️ Suspend a trip until further notice |
| 🏷️ 10% off for two travelers + codes `EID20` `YEAREND10` | 🎟️ Manage discount codes |
| 💳 Pay by card or Apple Pay | 📝 Update booking status |
| ✉️ Email at every step | |
| 🧾 Receipt: travel-day weather + itinerary + exchange rate | |
| 🔔 Welcome voice at login, airplane chime on the receipt | |

## 📝 User Stories

**As a customer, I can:**
- 🧑‍💼 register and log in, and get my customer ID and a welcome email
- 🌍 browse and search destinations, and see the live weather of each city
- 💰 enter my budget, days and travelers, and get matching trips with a day-by-day plan
- 🏷️ get 10% off when we are two travelers, or use a discount code like `EID20`
- 🎫 book a trip, pay by card or Apple Pay, and get a confirmation email
- ❌ cancel a booking and see how long the refund takes
- 🧾 view my receipt with the weather on my travel day, what I will visit and the exchange rate
- ⭐ get trip recommendations by type and length

**As a manager, I can:**
- 📊 see revenue, bookings by status and the top destinations
- 👥 see who booked, list customers, and delete a customer
- 🗺️ add, edit and delete destinations, or suspend a trip until further notice
- 📝 update a booking status (completed, cancelled with refund)
- 🎟️ create and switch discount codes for Eid and the end of the year

## 🚀 Run

```bash
python -m venv venv
source venv/Scripts/activate      # Windows (Git Bash / MSYS2)
python -m pip install -r requirements.txt
python main.py
```

🔑 Manager account: `admin` / `admin123`  


## 🎮 Usage

1. **Welcome menu:** `1` Login · `2` Register · `0` Exit
2. **Customer menu:** type the number of the action

| # | Action | # | Action |
|---|---|---|---|
| 1 | 🌍 Browse destinations | 6 | 📋 My bookings |
| 2 | ☀️ Details + live weather | 7 | 💳 Pay for a booking |
| 3 | 🔎 Search destinations | 8 | ❌ Cancel a booking |
| 4 | 💰 Plan a trip by budget | 9 | 🧾 View receipt |
| 5 | 🎫 Book a trip | 10 | ⭐ Recommendations |

3. **Manager menu:**

| # | Action | # | Action |
|---|---|---|---|
| 1 | 📊 Dashboard | 7 | ➕ Add destination |
| 2 | 📋 All bookings | 8 | ✏️ Edit destination |
| 3 | 📝 Update booking status | 9 | 🗑️ Delete destination |
| 4 | 👥 List customers | 10 | ⏸️ Suspend / resume a trip |
| 5 | 🗑️ Delete a customer | 11 | 🎟️ Discount codes |
| 6 | 🗺️ List destinations | 0 | 🚪 Logout |

**Example: plan and book a trip**
1. Register (`2`), or log in (`1`).
2. Type `4`, enter a budget like `20000`, press Enter for 7 days, and pick a trip.
3. Type `y` to book, enter a date like `2026-12-25`, and a code like `EID20` (or `no`).
4. Pay with `card`, then type `9` to see your receipt. 🎉

## 🖥️ Sample output

```text
╭───────────────────────── SkyRoute Receipt ──────────────────────────╮
│ Reference: SR-0006-D72E                                             │
│ Customer:  MohammedAlnsafi                                          │
│ Trip:      🇹🇷 Istanbul, Turkey                                      │
│ Date:      2026-12-25  (7 days, 1 traveler(s), luxury)              │
│ Payment:   card                                                     │
│ Status:    confirmed                                                │
│                                                                     │
│   Flights                      1,200 SAR                            │
│   Hotel                        3,240 SAR                            │
│   Food                         1,512 SAR                            │
│   Transport                      280 SAR                            │
│   Activities                   1,260 SAR                            │
│   Code YEAREND10 (10%)          -749 SAR                            │
│   --------------------------------------                            │
│   TOTAL PAID                   6,743 SAR                            │
│                                                                     │
│ Currency: Turkish lira (TRY): 1 SAR = 10.93 TRY (approx.)           │
│                                                                     │
│ Weather on 2026-12-25: no forecast yet                              │
│ Best season: Apr-Jun, Sep-Nov                                       │
│                                                                     │
│ What you will visit (7 days)                                        │
│   Day 1: Arrive in Istanbul, check in and relax                     │
│   Day 2: Hagia Sophia                                               │
│   Day 3: Grand Bazaar                                               │
│   Day 4: Bosphorus cruise                                           │
│   Day 5: Galata Tower                                               │
│   Day 6: Hagia Sophia                                               │
│   Day 7: Last-minute shopping and departure                         │
│                                                                     │
│ Company email: support@skyroute.example                             │
╰─────────────────────────────────────────────────────────────────────╯
```

🎨 Colors: 🟢 success · 🔴 error · 🟡 warning · 🔵 info  
↩️ Type `b` at any question to go back.

## 🗂️ Structure

```text
main.py            ▶️ entry point
agency/
├── models/        📦 data (User, Country, Booking)
├── services/      🧠 logic (booking, payment, weather, currency, email)
├── ui/            🖥️ screens and menus
├── storage/       💾 JSON files
├── utils/         🛡️ encryption, validation, sound
└── sounds/        🔔 airplane chime
tests/             🧪 179 tests
```

## 🧪 Tests

```bash
python -m unittest discover -s tests
```

## 🔒 Security
- 🔐 Passwords: PBKDF2 hash + salt
- 🗝️ The users file `data/users.json` is encrypted (Fernet); the key is in `data/secret.key`
- 💳 Card details are only checked, never saved
- 🙈 `.env`, `data/` and `venv/` are never uploaded to GitHub

## ⚙️ Email (optional)
Copy `.env.example` to `.env` and fill in your Gmail details (App Password), then check:

```bash
python main.py --test-email your_address@gmail.com
```

Without `.env`, emails are saved in `data/outbox/`.

## 📚 Libraries
`rich` 🎨 · `pyfiglet` 🔠 · `cryptography` 🔐 · everything else is the Python standard library.

> 💡 Prices and exchange rates are rough estimates for learning purposes.

## 👨‍💻 Developer
**Mohammed Alnsafi** 🚀  
Python course unit project: SkyRoute ✈️