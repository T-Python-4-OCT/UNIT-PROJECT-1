# Riyadh Smart Trip 🚗

## Overview

Riyadh Smart Trip is an interactive Python CLI application designed to help users plan trips within Riyadh, Saudi Arabia.

The application estimates trip duration based on the user's starting location, destination, departure time, and simulated traffic conditions. Its goal is to demonstrate how Python can be used to build a simple trip-planning tool.

**Note:** The current version uses simulated traffic data and user-provided base travel durations. It does not provide real-time traffic information or actual navigation routes.

## Features & User Stories

### As a user, I should be able to:

- Plan a trip by entering a starting location and destination.
- Enter my preferred departure time.
- Provide an estimated base travel duration.
- Receive an estimated trip duration based on simulated traffic conditions.
- View the expected traffic period, such as morning peak or off-peak.
- Receive clear error messages when entering invalid information.
- Save planned trips and view previously saved trips (once storage functionality is implemented).

## Usage

Run the application from the terminal:

```bash
python main.py
```

Follow the interactive menu to select an available action.

For example, to plan a trip, enter:

- Starting location: Al Narjis
- Destination: KAFD
- Departure time: 08:30
- Estimated base duration: 20 minutes

The application calculates an estimated duration using the simulated traffic factor for the selected departure time.

## Project Structure

```text
Riyadh-Smart-Trip/
├── main.py
├── traffic_data.py
├── trips.py
├── storage.py
├── trips.json
├── requirements.txt
└── README.md
```

The project is organized into separate Python modules to keep the application logic maintainable and easy to understand. The structure will be updated as development progresses.

## Technologies Used

- Python
- Git
- GitHub
- JSON for data storage (planned)

## Installation

1. Clone or download the repository.
2. Open a terminal in the project directory.
3. Run the application:

```bash
python main.py
```

## Future Improvements

- Store and retrieve trip history.
- Compare estimated durations across different departure times.
- Integrate a suitable maps or traffic API.
- Improve trip summaries and reporting.

## Project Status

In Development

## Author

Muath Mohammad Sufani
