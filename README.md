# 🌍 Travel Explorer

## 📌 Overview

Travel Explorer is an interactive Python CLI application that helps users explore countries and discover travel destinations.

Users can browse countries by continent, view destination information, check live weather and currency rates, view public holidays, save favorite countries, and receive personalized destination recommendations.

## ✨ Features

- 🌎 Explore countries by continent
- 📖 View country information
- 🍣 Discover famous foods
- 🎉 Explore events and experiences by city
- 🏯 Discover famous places by city
- 🌤️ Check live weather
- 💰 View currency and exchange rates
- 📅 View public holidays
- ⭐ Save and manage favorite countries
- ✈️ Get personalized destination recommendations
- ↩️ Navigate between menus using the Back option
- ✅ Input validation and error handling

## 👤 User Stories

As a traveler, I should be able to:

- Browse countries by continent.
- Explore information about a selected country.
- View famous foods, places, and experiences.
- Check live weather for supported cities.
- View currency and public holidays.
- Save and remove favorite countries.
- Get destination recommendations based on my interests.
- Return to previous menus.
- Receive clear messages when entering invalid input.

## 📁 Project Structure

```text
UNIT-PROJECT-1/
│
├── main.py
├── countries.py
├── weather.py
├── currency.py
├── holiday_calendar.py
├── recommendations.py
├── favorites.py
├── destination_info.py
├── favorites.json
├── requirements.txt
└── README.md
```

## ⚙️ Installation

```bash
git clone <repository-url>
cd UNIT-PROJECT-1
python -m venv venv
```

Activate the virtual environment and install the required packages:

```bash
pip install -r requirements.txt
```

## ▶️ Run the Project

```bash
python main.py
```

## 📚 Usage

From the main menu, users can:

```text
1. Explore a Country
2. Find My Destination
3. Favorites
4. Exit
```

Select a country to access its information, foods, events, places, weather, currency, holidays, and favorites.

The recommendation system allows users to select their interests and receive suitable destination suggestions.

## 📦 Requirements

The project uses Python and external packages including:

- `requests`
- `holidays`

The exact versions are listed in `requirements.txt`.

## 🎯 Project Goals

- Apply Python programming concepts in a practical project.
- Practice functions, loops, conditions, and data structures.
- Build a modular and maintainable CLI application.
- Work with APIs and external libraries.
- Practice Git and GitHub.
- Build useful recommendation features.

## 👨‍💻 Author

**Abdulrahman Habeb Alsuhemi**