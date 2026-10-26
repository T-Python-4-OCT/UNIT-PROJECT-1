# Riyadh Smart Trip 🚗🚇

An interactive Python command-line app that helps you plan trips in Riyadh and compare the **car** with the **metro**.

> **Note:** Routes, traffic conditions, metro fares and fuel costs are **estimates** based on sample data. The app does not use live traffic or navigation.

## Overview

Enter a start, a destination and a departure time. The app estimates the car trip using simulated traffic for that time of day, finds a matching metro route using real station data, and recommends the best option for your priority: fastest, cheapest, or a balance of both. Trips can be saved, viewed, updated and deleted.

## User Stories

As a traveler, I can:

- plan a trip and see the traffic period and estimated car duration.
- compare car and metro duration and cost for the same trip.
- choose a priority (fastest, lowest cost, best balance) and get a recommendation.
- see a chart comparing car and metro duration.
- save, view, update and delete my trips.
- see a report with the average duration and the fastest car and metro trips.
- enter my arrival time and get a suggested departure time.
- get clear messages when my input is invalid or a route is not available.

## Features

| Feature | Description |
|---|---|
| Plan a trip | Enter locations and time, get a summary and comparison, and save it |
| Transport comparison | Car (duration, fuel cost) vs. metro (line, stations, duration, fare) |
| Recommendation | Based on the priority you choose |
| Chart | Matplotlib bar chart of car vs. metro duration |
| Trip management | Save, view, update and delete trips (JSON file) |
| Reports | Trip statistics and a Riyadh traffic report |
| Departure suggestion | Latest departure time that arrives on time |
| Input validation | Time format, empty locations, trip numbers, missing data files |

## Installation

```bash
git clone https://github.com/muathhhh/UNIT-PROJECT-1
cd UNIT-PROJECT-1
python -m venv venv
source venv/bin/activate        # Windows (Git Bash): source venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

On Windows PowerShell or CMD, activate with `venv\Scripts\activate`.

## Usage

Type the option number from the menu and press Enter.

| Option | What it does |
|---|---|
| 1 | Plan a trip, compare transport, and save |
| 2 | View saved trips |
| 3 | View the trip report and traffic report |
| 4 | Update the departure time of a saved trip |
| 5 | Delete a saved trip |
| 6 | Compare car and metro for any available route |
| 7 | Suggest a departure time for a desired arrival time |
| 8 | Exit |

**Example** (option 6):

```
Enter starting location: KAFD
Enter destination: National Museum
Enter departure time (HH:MM): 08:00
```

Then choose a priority. The app shows the car and metro estimates, a recommendation, and a chart. Close the chart window to return to the menu.

Other routes with a metro comparison: `Al Wurud` → `KAFD`, `King Saud University` → `King Fahad Sport City`.

**Tips:**
- Locations are not case-sensitive.
- The route must exist in the sample data (`routes.json`).
- Neighborhoods like `Al Narjis` are car routes only, so the metro shows "Route unavailable".

## Project Structure

```
├── main.py                 # Menu and user interaction
├── trips.py                # Trip planning
├── transport_advisor.py    # Car vs. metro comparison and recommendation
├── metro_data.py           # Metro stations and route estimation
├── traffic_data.py         # Traffic periods and duration estimation
├── traffic_stats.py        # Traffic report
├── storage.py              # Save, load, update, delete trips
├── models.py               # Trip class
├── trip_charts.py          # Matplotlib chart
├── routes.json             # Sample car routes
├── locations.json          # Metro stations (RCRC Open Data)
├── traffic_stats.json      # Traffic statistics sample
├── tests/                  # Unit tests
└── requirements.txt
```

Saved trips are stored in `trips.json`, which is created when you save your first trip and is not tracked by Git.

## Running the Tests

```bash
python -m unittest
```

## Limitations

- Traffic is simulated, not live.
- Routes come from sample data.
- Metro duration and fares are estimates.
- Metro routes work on **one line only** (no transfers).
- Car cost covers fuel only.

## Future Improvements

- Use a real-time traffic or maps API.
- Support metro transfers.
- Link neighborhoods to their nearest metro station.
- Add more routes and more accurate fares.

## Author

Muath Mohammad Sufani
