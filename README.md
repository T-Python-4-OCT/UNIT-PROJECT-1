# 🏥 SmartClinic Reception CLI

## Overview
SmartClinic Reception is an interactive command-line system for a clinic's **front desk**, written in Python.
The receptionist logs in and manages everything the reception handles: patients, clinics (each with a doctor,
fee and working hours), appointments, check-in, invoices and daily reports.

Smart features:
- **Nearest free slot**: finds the first free appointment in a clinic and can book it for a patient in one step.
- **No double booking**: a clinic slot, or a patient's time, can never be booked twice.
- **Recall list**: shows patients who have not visited for 6+ months so the receptionist can call them.
- **Validation**: phone numbers, ages, dates and times are checked; duplicates are rejected.
- **Safe deletes**: patients/clinics that have appointments on record cannot be deleted.
- **Persistent storage**: data is saved as JSON files; passwords are stored as SHA-256 hashes.
- **Colourful output** using the `rich` library (falls back to plain text if it is not installed).

## Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows (PowerShell/CMD)   |  source venv/bin/activate  (Linux/Mac)
pip install -r requirements.txt
python main.py
```
Requires Python 3.8+. Demo data is created automatically on the first run.

Login: **`sultan`** / **`1234`**

## User Stories
As a receptionist I can:
- Register a new patient and edit or delete patient records
- Search patients by name or phone and open a patient file with visit history
- Add a clinic (doctor, fee), change its fee and set its working hours, or remove it
- See a clinic's free slots and find the nearest free slot
- Book, cancel and reschedule appointments for patients
- See the appointments of any day
- Check a patient in and mark a visit as completed
- Print an invoice for a visit (with 15% VAT)
- See the daily report (visits, cancellations, revenue, busiest clinic)
- See which patients should be called back (no visit for 6+ months)

## Usage
Dates are `YYYY-MM-DD`, times are `HH:MM`. Patients can be referenced by **ID, phone, or name** (if unique).
Clinics by **ID or name** (use quotes for names with spaces). Type `help` for the list, `logout` or `exit` to leave.

| Command | Description |
|---|---|
| `add_patient` | Register a new patient (interactive) |
| `patients` / `search <name\|phone>` | List / search patients |
| `patient <id\|phone\|name>` | Patient file + visit history |
| `edit_patient <id> <field> <value>` | Edit `name`, `phone`, `age`, `blood`, `allergies`, `notes` |
| `delete_patient <id>` | Delete a patient |
| `recall` | Patients not seen for 6+ months |
| `add_clinic` / `clinics` | Add / list clinics |
| `clinic_fee <clinic> <fee>` | Change the consultation fee |
| `hours <clinic>` / `set_hours <clinic> <day> <start> <end>` or `off` | Working hours |
| `remove_clinic <clinic>` | Remove a clinic |
| `slots <clinic> [date]` | Free slots |
| `next_available <clinic> [patient]` | Nearest slot (and book it for the patient) |
| `book <patient> <clinic> <date> <time>` | Book an appointment |
| `cancel <id>` / `reschedule <id> <date> <time>` | Cancel / move an appointment |
| `appointments [date]` | Appointments of a day (default today) |
| `checkin <id>` / `done <id>` | Check in / complete a visit |
| `invoice <id>` | Print an invoice |
| `report [today\|date]` | Daily report |

### Example
```
sultan@clinic > add_patient
sultan@clinic > next_available cardiology sara        # shows the nearest slot, asks to book
sultan@clinic > book faisal general 2026-11-01 10:00
sultan@clinic > checkin 3
sultan@clinic > done 3
sultan@clinic > invoice 3
sultan@clinic > report today
```

## Project Structure
```
smartclinic/
├── main.py                 # entry point (login menu)
├── models/                 # dataclasses: Receptionist, Patient, Clinic, Appointment
├── services/               # logic: auth, patients, clinics, appointments, billing
├── storage/                # JSON persistence + demo data seed
├── ui/                     # CLI shell + reception menu
├── utils/                  # validators, formatters (rich), errors
├── data/                   # JSON data files (created automatically)
└── tests/                  # unit tests
```

## Tests
```bash
python -m unittest discover -s tests -t .
```

## Future Improvements
- Salted password hashing (bcrypt) and multiple receptionist accounts
- SMS reminders for appointments
- SQLite instead of JSON files