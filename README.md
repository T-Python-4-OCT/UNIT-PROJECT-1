# Riyadh Smart Trip 🚗

## Overview

Riyadh Smart Trip is an interactive Python CLI application designed to help users plan trips within Riyadh, Saudi Arabia.

The application estimates driving duration using simulated traffic conditions and compares estimated car and metro travel options. It also provides trip reports and departure-time suggestions to help users make more informed travel decisions.

**Note:** This project uses sample route data and simulated traffic conditions. Metro durations and fares are sample estimates, and car costs represent estimated fuel costs only. The application does not provide real-time traffic data or live navigation.

## Features

- **Trip Planning:** Plan trips by entering a starting location, destination, and departure time.
- **Traffic Estimation:** Estimate driving duration based on simulated traffic periods.
- **Trip Storage:** Save and view previously planned trips using JSON files.
- **Trip Management (CRUD):** Create, view, update, and delete saved trips.
- **Transport Comparison:** Compare estimated car and metro travel times and costs.
- **Smart Trip Summary:** Display time and cost differences and recommend an option based on the selected priority.
- **Departure-Time Suggestions:** Suggest a departure time based on a desired arrival time and estimated driving duration.
- **Trip Reports:** View saved-trip statistics, average duration, fastest car trip, and fastest saved metro trip.
- **Input Validation:** Handle invalid menu choices, trip numbers, and time inputs.

## Technologies Used

- Python
- JSON for data storage
- Git and GitHub
- Python modules and functions
- Object-Oriented Programming (OOP)

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

The application is organized into separate modules to improve readability, maintainability, and separation of responsibilities.

- `main.py`: Displays the menu and coordinates user actions.
- `models.py`: Defines the `Trip` class.
- `trips.py`: Handles trip planning.
- `storage.py`: Manages saving, loading, updating, and deleting trips.
- `traffic_data.py`: Estimates driving duration using simulated traffic periods.
- `traffic_stats.py`: Generates traffic-related reports.
- `transport_advisor.py`: Compares transport options and generates smart trip recommendations.
- `routes.json` and `locations.json`: Store sample route and location data.
- `trips.json`: Stores saved trips.

## Installation and Usage

### Requirements

- Python 3 installed
- Git (optional, for cloning the repository)

### Run the Application

1. Clone or download the repository.
2. Open a terminal in the project directory.
3. Run:

```bash
python main.py
```

4. Follow the interactive menu.

### Main Menu

1. Plan a Trip
2. View Saved Trips
3. View Trip Report
4. Update a Trip
5. Delete a Trip
6. Compare Transport Options
7. Suggest Departure Time
8. Exit

### Example

A user can select a route such as Al Narjis to KAFD, enter a departure time, and view an estimated driving duration based on the project's sample traffic data.

The user can then compare transport options, choose a priority (fastest, lowest cost, or balanced), and view a smart trip summary.

## Limitations

- Traffic conditions are simulated and are not based on live traffic feeds.
- Route information depends on the available sample data.
- Metro duration and fare values are illustrative estimates.
- Estimated car costs cover fuel only and do not include parking or other vehicle expenses.
- Recommendations depend on the assumptions and sample data used by the application.

## Future Improvements

- Integrate a reliable maps or traffic API.
- Improve route-specific metro duration and fare estimates.
- Add more sample routes and transport options.
- Expand input validation and automated testing.

## Project Status

In Development

## Author

Muath Mohammad Sufani
```
