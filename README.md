# Riyadh Smart Trip 🚗

## Overview

Riyadh Smart Trip is an interactive Python command-line application that helps users plan trips within Riyadh, Saudi Arabia.

The application estimates car travel duration using simulated traffic conditions, compares car and metro travel options, suggests departure times, and provides trip reports. It also allows users to save, view, update, and delete planned trips.

**Important:** This project uses sample route data and simulated traffic conditions. Travel durations, metro fares, and fuel costs are estimates. The application does not provide real-time traffic data or live navigation.

## Features

### Trip Planning
- Enter a starting location, destination, and departure time.
- Calculate estimated travel duration based on the selected route and simulated traffic conditions.
- Display a trip summary and save planned trips.

### Traffic Estimation
- Identify the expected traffic period based on departure time.
- Estimate travel duration using predefined traffic factors.
- Suggest a departure time based on a desired arrival time.

### Trip Management (CRUD)
- **Create:** Save planned trips.
- **Read:** View saved trips and trip reports.
- **Update:** Modify saved trip information.
- **Delete:** Remove saved trips.

### Transport Comparison
- Compare estimated car and metro travel durations and costs.
- Choose a trip priority: fastest trip, lowest cost, or best balance between time and cost.
- Display a Smart Trip Summary with estimated differences and a recommendation.

### Reports
- View the total number of saved trips.
- Calculate the average estimated trip duration.
- Review available car and metro trip estimates.
- View traffic statistics based on the project's sample data.

### Input Validation
- Validate departure and arrival time formats.
- Check that required locations are provided.
- Display error messages for invalid input or unavailable sample routes.

## Technologies Used

- Python
- JSON for data storage
- Python modules and functions
- Object-Oriented Programming (OOP)
- Git and GitHub

## Project Structure

```text
Riyadh-Smart-Trip/
├── main.py
├── models.py
├── trips.py
├── storage.py
├── traffic_data.py
├── traffic_stats.py
├── transport_advisor.py
├── metro_data.py
├── routes.json
├── locations.json
├── transport_options.json
├── traffic_stats.json
├── trips.json
├── .gitignore
└── README.md
```

## Installation and Usage

1. Clone or download the repository.
2. Open a terminal in the project directory.
3. Run the application:

```bash
python main.py
```

4. Follow the interactive menu to select an action.

The application menu includes trip planning, viewing saved trips, trip reports, updating and deleting trips, comparing transport options, and suggesting departure times.

## Limitations

- Traffic conditions are simulated and are not retrieved from a live traffic service.
- Route information is based on the project's sample data.
- Metro travel durations and fares are sample estimates.
- Car costs estimate fuel expenses only and do not include parking, tolls, or other expenses.
- The application does not provide live maps or turn-by-turn navigation.

## Future Improvements

- Integrate a real-time traffic or mapping API.
- Improve route-specific metro duration and fare estimates.
- Expand the sample route database.
- Add automated tests and further input validation.

## Project Status

In Development

## Author

Muath Mohammad Sufani
```

```

بهذا ترفع **تعديل الـ README فقط**، وتترك تعديلات `main.py` و`storage.py` وملفات الرحلات الأخرى محليًا إلى أن نتأكد منها ونقرر رفعها.
