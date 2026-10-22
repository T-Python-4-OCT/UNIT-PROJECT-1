# UNIT PROJECT 1: Smart Irrigation Planner
 
A command-line application that helps farmers decide **when** and **how much** to irrigate each crop, using live weather data and the FAO water requirement method. It aims to reduce water waste and cost in arid regions such as Hail, Saudi Arabia.
 
## Overview
 
The farmer registers a farm and its crops. The program fetches real weather data over the internet, calculates each crop's daily water need, applies smart rules (such as postponing irrigation before rain), and reports how much water and money were saved compared to a traditional fixed schedule.
 
There are two types of users: a **Farmer** and a **Manager**.
 
## Features
 
- Interactive, color-coded CLI menu
- Add, edit, delete, and search farms and crops
- Live weather and evapotranspiration (ET0) data, with an offline fallback to the last saved data
- Water requirement calculation per crop
- Weekly irrigation schedule in formatted tables
- Smart alerts: rain expected, heat wave, frost risk, strong wind, over-irrigation
- Savings report (m3 and SAR) compared to traditional irrigation
- Data saved in JSON files, with input validation and clear error messages

## User Stories
 
**As a Farmer, I can:**
- Register my farm and add, edit, or delete crops.
- Search for a crop and view its water needs.
- View the current weather and forecast.
- Get a weekly irrigation schedule with water volume and best time.
- Receive alerts for heat, frost, wind, and rain.
- Log my actual irrigation.
- View a savings report.

**As a Manager, I can:**
- Add, edit, or delete crop types in the database.
- View statistics: most planted crops, total water used and saved.
- Update settings such as the water price per m3.

## Project Structure
 
```
smart_irrigation/
├── main.py
├── menus/
│   ├── farm_menu.py
│   ├── weather_menu.py
│   ├── report_menu.py
│   └── manager_menu.py
├── models/
│   ├── crop.py
│   └── farm.py
├── services/
│   ├── weather.py
│   ├── water_calculator.py
│   ├── scheduler.py
│   ├── alerts.py
│   └── reports.py
├── utils/
│   ├── file_handler.py
│   ├── validators.py
│   ├── display.py
│   └── ui_helpers.py
├── data/
│   ├── crops.json
│   ├── farms.json
│   └── settings.json
├── requirements.txt
└── README.md

```
 
## Installation
 
 
```bash
git clone https://github.com/<username>/<repo-name>
cd <repo-name>
 
python -m venv venv
 
source venv/Scripts/activate     # Mac & Linux: source venv/bin/activate  
 
pip install -r requirements.txt

```
 
## Usage
 
Type the number of an option and press Enter.
 
```
===== Smart Irrigation Planner =====
1. Manage Farm
2. Manage Crops
3. View Weather
4. Get Irrigation Schedule
5. Log Irrigation
6. View Savings Report
7. Manager Panel
8. Exit
```
 
| Option | Description |
|---|---|
| 1. Manage Farm | Create your farm and set its name and city |
| 2. Manage Crops | Add, edit, delete, list, or search crops |
| 3. View Weather | Show current weather and forecast |
| 4. Get Irrigation Schedule | Weekly schedule with water volume |
| 5. Log Irrigation | Record the irrigation you actually performed |
| 6. View Savings Report | Compare your usage with traditional irrigation |
| 7. Manager Panel | Manage the crop database and view statistics |
| 8. Exit | Save and quit |
 
**Example workflow:** create a farm (option 1), add `Wheat` with 1000 m2 (option 2), check the weather (option 3), get the schedule (option 4), log your irrigation (option 5), and view your savings (option 6).
 
## Libraries Used
 
**External libraries**
 
| Library | Purpose |
|---|---|
| `requests` | Sends HTTP requests to fetch live weather data |
| `colorama` | Adds colors to terminal messages (success, error, warning) |
| `tabulate` | Prints schedules and reports as formatted tables |
 
**Built-in Python modules**
 
| Module | Purpose |
|---|---|
| `json` | Saves and loads farm and crop data |
| `datetime` | Handles dates for schedules and logs |
| `os` / `pathlib` | Manages file paths |
 
## Author
 
Abdulaziz Ayed,
GitHub: [ftb2220-create](https://github.com/ftb2220-create)
