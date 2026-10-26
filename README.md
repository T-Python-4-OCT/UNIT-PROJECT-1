# ✈️ TripMate CLI
### Smart Travel Planner & Expense Manager

TripMate is a Python command-line application designed to help users plan trips, manage travel expenses, check weather conditions, and receive AI-powered destination recommendations.

The project combines core Python concepts with external APIs, persistent JSON storage, data validation, reporting, and modular application design.

---

## 🌍 Overview

Planning a trip usually involves several separate tasks such as:

- Choosing a destination
- Managing a travel budget
- Tracking expenses
- Checking weather conditions
- Searching for suitable destinations

TripMate brings these features together in one interactive CLI application.

The application allows users to create and manage trips, record expenses, monitor their budget, check weather forecasts, export reports, and use Gemini AI to receive personalized destination recommendations.

---

## ✨ Main Features

### 🧳 Trip Management

Users can:

- Create a new trip
- View all saved trips
- View detailed trip information
- Update the destination
- Update travel dates
- Update the trip budget
- Delete a trip
- Automatically delete related expenses when a trip is deleted

---

### 💰 Expense Management

Each trip can have its own expenses.

Users can:

- Add expenses
- Edit expenses
- Delete expenses
- Categorize expenses
- Add expense dates
- View total spending
- View the remaining budget
- Receive warnings when spending exceeds the available budget

Supported expense categories include:

| Category |
|---|
| Accommodation |
| Transport |
| Food |
| Activities |
| Shopping |
| Other |

---

## 📊 Budget Reports

TripMate provides a detailed report for each trip.

The report includes:

- Total trip budget
- Total amount spent
- Remaining budget
- Budget usage percentage
- Expense breakdown by category
- Highest expense
- Highest spending category
- Planned daily budget
- Expense per planned trip day

The application also displays warnings when the user approaches or exceeds the trip budget.

---

## 📁 CSV Export

Trip reports can be exported to a `.csv` file.

The exported file contains:

- Trip destination
- Travel dates
- Trip budget
- Expense IDs
- Expense titles
- Expense categories
- Expense dates
- Expense amounts
- Total spending

CSV files can be opened using applications such as Microsoft Excel.

---

## 🌦️ Weather Integration

TripMate integrates with the **Open-Meteo API**.

It uses two services:

### Geocoding API

The application converts a city and country name into geographic coordinates.

### Weather Forecast API

The application can display:

- Current temperature
- Feels-like temperature
- Weather condition
- Humidity
- Wind speed
- Rain probability
- Maximum temperature
- Minimum temperature

TripMate also generates simple weather-based travel recommendations.

For example:

> Pack warm clothing.

or:

> There is a good chance of rain, so take an umbrella.

Forecast availability depends on how close the trip date is.

---

## 🤖 AI Travel Planner

TripMate integrates with the **Google Gemini API** to provide AI-powered travel recommendations.

The AI Travel Planner asks the user for:

- Departure country
- Departure city
- Total budget
- Trip duration
- Start date
- Preferred weather
- Preferred activities
- Travel style

Gemini then recommends up to three destinations based on the user's preferences.

Each recommendation includes:

- Destination
- Reason for recommendation
- Estimated budget suitability
- Suggested activities

> **Note:** Budget suitability is an AI-generated estimate and does not use live flight, hotel, or booking prices.

The user can select an AI recommendation and automatically create a new trip from it.

---

## 🧠 AI Location Correction

TripMate also uses Gemini to help correct destination names.

For example:

```text
User Input:
Country: saudi arabia
City: damam

AI Suggestion:
Dammam, Saudi Arabia
```

The corrected destination is then validated using the location service before it is accepted.

This helps prevent invalid locations from being stored.

---

## 🛡️ Input Validation

TripMate validates user input to reduce errors.

Validation includes:

- Empty text prevention
- Numeric validation
- Positive budget validation
- Positive expense validation
- Menu choice validation
- Date format validation
- Past and future date rules
- Start and end date validation
- Invalid location prevention
- Confirmation before destructive actions

The expected date format is:

```text
YYYY-MM-DD
```

Example:

```text
2026-12-01
```

---

## 💾 Data Storage

TripMate stores application data locally using JSON files.

```text
data/
├── trips.json
└── expenses.json
```

The application automatically creates the data files when necessary.

Trips and expenses are converted between Python objects and JSON using model methods such as:

```python
to_dict()
```

and:

```python
from_dict()
```

The application also uses safe file writing to reduce the risk of corrupting stored data.

---

## 🧱 Project Structure

```text
UNIT-PROJECT-1_/
│
├── data/
│   ├── trips.json
│   └── expenses.json
│
├── tripmate/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── colors.py
│   │   ├── config.py
│   │   ├── ui.py
│   │   ├── utils.py
│   │   └── validation.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── expenses.py
│   │   └── trip.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_helper.py
│   │   ├── storage.py
│   │   └── weather.py
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── ai_workflow.py
│   │   ├── expense_workflows.py
│   │   ├── location_workflow.py
│   │   └── trip_workflows.py
│   │
│   ├── __init__.py
│   ├── menu.py
│   └── reports.py
│
├── .env
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

---

## 🧩 Application Architecture

The project is divided into multiple modules to keep responsibilities separated and reduce code repetition.

| Folder / File | Responsibility |
|---|---|
| `core/` | Validation, configuration, UI helpers and shared utilities |
| `models/` | Trip and Expense data models |
| `services/` | JSON storage and external API integrations |
| `workflows/` | Interactive application workflows |
| `reports.py` | Trip reports and CSV export |
| `menu.py` | Main application menu |
| `main.py` | Application entry point |

This structure helps keep the project easier to maintain and understand.

---

## 🧑‍💻 Python Concepts Used

TripMate demonstrates several Python concepts covered during the course:

- Variables
- Conditional statements
- `for` loops
- `while` loops
- Functions
- Function parameters
- Return values
- Lists
- Dictionaries
- Classes
- Dataclasses
- Modules
- Packages
- File handling
- JSON
- Exception handling
- API requests
- Environment variables
- Input validation
- List comprehensions

---

## 🏗️ Classes

The project uses Python dataclasses for its main data models.

### Trip

The `Trip` class stores information such as:

```text
Trip ID
Country
City
Start Date
End Date
Budget
```

### Expense

The `Expense` class stores:

```text
Expense ID
Trip ID
Title
Category
Amount
Date
```

---

## 🔁 Reusable Functions

The project uses reusable functions to reduce repeated code.

Examples include:

```text
get_menu_choice()
get_yes_no()
get_date()
get_text_input()
format_money()
calculate_total_expenses()
find_location()
print_menu()
```

This makes the code easier to read and maintain.

---

## 🛠️ Technologies Used

| Technology | Usage |
|---|---|
| Python | Main programming language |
| Rich | CLI tables, colors and panels |
| Requests | HTTP API requests |
| Open-Meteo | Weather and location data |
| Google Gemini | AI travel recommendations |
| JSON | Persistent local storage |
| CSV | Report export |
| python-dotenv | Environment variable loading |
| Git | Version control |
| GitHub | Source code repository |

---

## 🔌 APIs Used

### Google Gemini API

Used for:

- AI destination recommendations
- Location spelling correction

### Open-Meteo Geocoding API

Used to:

- Search for real locations
- Validate destinations
- Retrieve latitude and longitude

### Open-Meteo Weather API

Used to:

- Retrieve current weather
- Retrieve trip forecasts
- Provide weather-based recommendations

---

## 📖 User Stories

### Trip Management

> As a traveler, I want to create and manage trips so that I can organize my travel plans.

### Expense Tracking

> As a traveler, I want to record my expenses so that I can monitor how much money I have spent.

### Budget Monitoring

> As a traveler, I want to compare my expenses against my budget so that I can avoid overspending.

### Weather Forecast

> As a traveler, I want to check the weather at my destination so that I can prepare for my trip.

### AI Recommendations

> As a traveler, I want personalized destination recommendations based on my budget and preferences so that I can discover suitable places to visit.

### Reports

> As a traveler, I want to view and export a trip report so that I can analyze my travel spending.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
```

Then enter the project directory:

```bash
cd UNIT-PROJECT-1_
```

---

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Optional:

```env
GEMINI_MODEL=gemini-3.5-flash-lite
```

> Never upload your `.env` file or API key to GitHub.

The `.env` file is excluded using `.gitignore`.

---

## ▶️ Run the Application

Run:

```bash
python main.py
```

The main menu will appear:

```text
================================
   TRIPMATE
================================
1. Create Trip
2. My Trips
3. Manage Trip
4. AI Travel Planner
5. Exit
```

---

## 🧭 Basic Usage

### Create a Trip

Choose:

```text
1. Create Trip
```

Then provide:

```text
Country
City
Start Date
End Date
Budget
```

---

### View Trips

Choose:

```text
2. My Trips
```

TripMate displays your trips in a table including:

```text
Destination
Dates
Budget
Spent
Remaining
Budget Used
```

---

### Manage a Trip

Choose:

```text
3. Manage Trip
```

Available options include:

```text
View Trip Details
Update Trip
Add Expense
Edit Expense
Delete Expense
Trip Report
Export Report
Check Weather
Delete Trip
```

---

### Use the AI Travel Planner

Choose:

```text
4. AI Travel Planner
```

Answer the questions and Gemini will generate destination recommendations.

A selected AI destination can be validated and saved directly as a new trip.

---

## 📦 Requirements

The main project dependencies are:

```text
google-genai
python-dotenv
requests
rich
```

They can be installed using:

```bash
pip install -r requirements.txt
```

---

## 🔒 Security

Sensitive information such as the Gemini API key is stored in:

```text
.env
```

The following files and folders are excluded from Git using `.gitignore`:

```text
.env
data/
exports/
.venv/
__pycache__/
*.pyc
```

---

## 🚀 Future Improvements

Possible future improvements include:

- Live flight search
- Live hotel information
- Currency conversion
- Database storage
- Graphical user interface
- User authentication
- More detailed travel itineraries

These features are outside the current project scope.

---

## 👨‍💻 Author

**Abdulrahman Al-Qahtani**

Computer Science Graduate  
Tuwaiq Academy — Web Development Track

---

## 📌 Project Type

**Tuwaiq Academy — Python Unit Project**

TripMate was developed to demonstrate Python fundamentals, modular programming, persistent data storage, API integration, validation, classes, functions, and practical problem solving.