# 🚨 Crisis Management & Logistics Simulator

A command-line command center for emergency response. Field teams report urgent needs, dispatchers turn them into
shipments from the supply inventory, and fleet officers assign vehicles (after checking live weather) and track
deliveries. Everything runs in the terminal with a neon "control room" interface built with
[Rich](https://github.com/Textualize/rich).

## Features

- Role-based accounts: **Manager, Dispatcher, Field Supervisor, Fleet Officer, General User**
- Arrow-key menus (↑/↓ + Enter, or press the option number)
- Supply inventory with low-stock warnings
- Field requests with priorities, linked end-to-end to the shipment that answers them
- Shipment lifecycle: `Pending Fleet Assignment → In Transit → Completed`
- Live weather per region (Open-Meteo API, no key needed) with a high-wind warning for drones
- Smart supply recommendations by crisis category
- Vehicle capacity and maintenance checks before dispatch, with an animated dispatch screen
- Passwords hashed with scrypt, email validation, masked password entry, password rules

## User stories

**Manager** — view the inventory, add supply items, watch every shipment, list users, create Manager / Dispatcher accounts.
**Dispatcher** — read field requests (most urgent first), check weather, get recommendations, create a shipment for a request.
**Field Supervisor** — report an urgent need with a priority, and track the status of my zone's requests.
**Fleet Officer** — see pending shipments, check destination weather, pick a vehicle, and mark shipments delivered.
**General User** — view the inventory.

## How a request flows

```
Field Supervisor ──► request (Pending)
Dispatcher       ──► shipment created for it (request: Approved, stock reduced)
Fleet Officer    ──► vehicle assigned (request + shipment: In Transit)
Fleet Officer    ──► marked delivered (request + shipment: Completed)
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env           # then edit the admin username/password
python main.py
```

The first start upgrades old data files automatically (and hashes any plain-text passwords), so back up `data/` once if
you have data you care about.

## Usage

| Where | Keys |
| --- | --- |
| Any menu | ↑ / ↓ to move, **Enter** to open, or type the option number |
| Read-only screens | any key goes back |
| Anywhere | **Ctrl+C** quits cleanly |

- **Admin login:** the username/password in your `.env` (`ADMIN_USERNAME`, `ADMIN_PASSWORD`).
- **Register New User** (main menu) creates Field Supervisor, Fleet Officer or General accounts.
  A logged-in manager creates Manager and Dispatcher accounts (Manager menu → option 5).
- **Password rules:** at least 8 characters, one UPPERCASE and one lowercase letter. Emails must look like `name@example.com`.

## Project structure

```
main.py                     menus for every role
src/
  config.py                 paths, regions, fleet, roles, status names
  flows.py                  interactive screens (questions + answers)
  models/                   User (+ roles), SupplyItem, Shipment, FieldRequest
  services/
    auth_service.py         accounts, login, hashing
    logistics_service.py    supplies, requests, shipments (no input()/print(), fully tested)
    migrations.py           upgrades old JSON files once
    recommend_service.py    smart recommendations
    weather_api.py          Open-Meteo client
  utils/
    display.py              Rich tables, menus, masked input, progress bars
    json_handler.py         UTF-8, atomic JSON read/write
    security.py             scrypt hashing, email/password validation
data/                       JSON "database"
```



## Security notes

- Passwords are stored as salted scrypt hashes; the admin password comes from `.env` (never commit it).
- `.env` is git-ignored; share `.env.example` instead.
- JSON files are written atomically, and a corrupt file is renamed to `*.corrupt` instead of being overwritten.