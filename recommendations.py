
import requests
import time

from countries import COUNTRIES


# ============================================================
# COLORS
# ============================================================

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
BLUE = "\033[94m"
WHITE = "\033[97m"
RESET = "\033[0m"


# ============================================================
# TRAVEL INTERESTS
# ============================================================

INTERESTS = {
    "1": "Rainy Weather",
    "2": "Cold Weather",
    "3": "Warm Weather",
    "4": "Beaches",
    "5": "Nature",
    "6": "Cities",
    "7": "Food",
    "8": "Snow",
}


# ============================================================
# DESTINATION CATEGORIES
# ============================================================

BEACH_CITIES = {
    "Jeddah",
    "Dubai",
    "Doha",
    "Miami",
    "Vancouver",
    "Cancun",
    "Rio de Janeiro",
    "Barcelona",
    "Nice",
    "Sydney",
    "Auckland",
    "Fiji",
    "Bangkok",
    "Kuala Lumpur",
    "Cape Town",
}


NATURE_CITIES = {
    "Vancouver",
    "Toronto",
    "Zurich",
    "Interlaken",
    "Queenstown",
    "Cape Town",
    "Nairobi",
    "Auckland",
    "Fiji",
    "Kyoto",
    "Madinah",
}


FOOD_CITIES = {
    "Tokyo",
    "Osaka",
    "Seoul",
    "Bangkok",
    "Kuala Lumpur",
    "Paris",
    "Rome",
    "Istanbul",
    "Barcelona",
    "Madrid",
    "Dubai",
    "New York",
    "Mexico City",
    "Buenos Aires",
}


CITY_CITIES = {
    "Tokyo",
    "Osaka",
    "Seoul",
    "London",
    "Paris",
    "Berlin",
    "Rome",
    "Madrid",
    "Amsterdam",
    "Dubai",
    "Riyadh",
    "Jeddah",
    "New York",
    "Toronto",
    "Mexico City",
    "Sao Paulo",
    "Sydney",
    "Melbourne",
}


# ============================================================
# OPEN-METEO WEATHER CODES
# ============================================================

RAIN_CODES = {
    51, 53, 55,
    56, 57,
    61, 63, 65,
    66, 67,
    80, 81, 82,
    95, 96, 97, 99,
}


SNOW_CODES = {
    71,
    73,
    75,
    77,
    85,
    86,
}


# ============================================================
# SHOW INTERESTS
# ============================================================

def show_interests():
    print()

    print(
        MAGENTA
        + "╔══════════════════════════════════════════════╗"
        + RESET
    )

    print(
        MAGENTA
        + "║          🤖 FIND MY DESTINATION             ║"
        + RESET
    )

    print(
        MAGENTA
        + "╚══════════════════════════════════════════════╝"
        + RESET
    )

    print()

    print(
        CYAN
        + "Choose your travel interests:"
        + RESET
    )

    print()

    for number, interest in INTERESTS.items():
        print(
            f"  {YELLOW}{number}{RESET}. "
            f"{interest}"
        )

    print(
        f"  {YELLOW}0{RESET}. ↩️ Back"
    )

    print()

    print(
        WHITE
        + "Example: 2,5,7"
        + RESET
    )


# ============================================================
# CHOOSE INTERESTS
# ============================================================

def choose_interests():
    show_interests()

    while True:

        choice = input(
            YELLOW
            + "\n➜ Choose interests separated by commas: "
            + RESET
        ).strip()

        if choice == "0":
         return None

        choices = [
            item.strip()
            for item in choice.split(",")
        ]

        valid_choices = []

        for item in choices:

            if item in INTERESTS:

                if item not in valid_choices:
                    valid_choices.append(item)

        if valid_choices:
            return valid_choices

        print()

        print(
            RED
            + "❌ Invalid selection."
            + RESET
        )

        print(
            WHITE
            + "Please choose numbers from 1 to 8."
            + RESET
        )


# ============================================================
# GET ALL CITIES
# ============================================================

def get_all_cities():
    cities = []

    for country_name, country in COUNTRIES.items():

        for city in country["cities"].values():

            city_data = {
                "country": country_name,
                "flag": country["flag"],
                "name": city["name"],
                "latitude": city["latitude"],
                "longitude": city["longitude"],
            }

            cities.append(city_data)

    return cities


# ============================================================
# GET LIVE WEATHER
# ============================================================

def get_live_weather(cities):

    if not cities:
        return []

    latitudes = ",".join(
        str(city["latitude"])
        for city in cities
    )

    longitudes = ",".join(
        str(city["longitude"])
        for city in cities
    )

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "weather_code"
        ),
        "timezone": "auto",
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            data = [data]

        results = []

        for city, weather in zip(cities, data):

            current = weather.get("current")

            if not current:
                continue

            results.append(
                {
                    "country": city["country"],
                    "flag": city["flag"],
                    "city": city["name"],
                    "temperature": current[
                        "temperature_2m"
                    ],
                    "humidity": current[
                        "relative_humidity_2m"
                    ],
                    "weather_code": current[
                        "weather_code"
                    ],
                }
            )

        return results

    except requests.RequestException:

        return []


# ============================================================
# SCORE WEATHER
# ============================================================

def score_weather(weather, interest):

    temperature = weather["temperature"]

    weather_code = weather["weather_code"]

    # Rainy
    if interest == "1":

        if weather_code in RAIN_CODES:
            return 30

        return 0

    # Cold
    if interest == "2":

        if temperature <= 10:
            return 30

        if temperature <= 18:
            return 20

        if temperature <= 23:
            return 10

        return 0

    # Warm
    if interest == "3":

        if 20 <= temperature <= 30:
            return 30

        if 18 <= temperature <= 35:
            return 20

        if 15 <= temperature <= 38:
            return 10

        return 0

    # Snow
    if interest == "8":

        if weather_code in SNOW_CODES:
            return 40

        if temperature <= 5:
            return 30

        if temperature <= 10:
            return 20

        if temperature <= 15:
            return 10

        return 0

    return 0


# ============================================================
# SCORE CITY
# ============================================================

def score_city(weather, interest):

    city = weather["city"]

    # Beaches
    if interest == "4":

        if city in BEACH_CITIES:
            return 30

        return 0

    # Nature
    if interest == "5":

        if city in NATURE_CITIES:
            return 30

        return 0

    # Cities
    if interest == "6":

        if city in CITY_CITIES:
            return 30

        return 0

    # Food
    if interest == "7":

        if city in FOOD_CITIES:
            return 30

        return 0

    return 0


# ============================================================
# CALCULATE SCORE
# ============================================================

def calculate_score(weather, selected_interests):

    total_score = 0

    for interest in selected_interests:

        total_score += score_weather(
            weather,
            interest,
        )

        total_score += score_city(
            weather,
            interest,
        )

    return total_score


# ============================================================
# GET MATCH REASONS
# ============================================================

def get_match_reason(weather, selected_interests):

    reasons = []

    temperature = weather["temperature"]

    weather_code = weather["weather_code"]

    city = weather["city"]

    for interest in selected_interests:

        # Rain
        if interest == "1":

            if weather_code in RAIN_CODES:
                reasons.append(
                    "Rainy weather"
                )

        # Cold
        elif interest == "2":

            if temperature <= 18:
                reasons.append(
                    "Cold weather"
                )

        # Warm
        elif interest == "3":

            if 20 <= temperature <= 30:
                reasons.append(
                    "Warm weather"
                )

        # Beaches
        elif interest == "4":

            if city in BEACH_CITIES:
                reasons.append(
                    "Beach destination"
                )

        # Nature
        elif interest == "5":

            if city in NATURE_CITIES:
                reasons.append(
                    "Nature destination"
                )

        # Cities
        elif interest == "6":

            if city in CITY_CITIES:
                reasons.append(
                    "Major city"
                )

        # Food
        elif interest == "7":

            if city in FOOD_CITIES:
                reasons.append(
                    "Great food destination"
                )

        # Snow
        elif interest == "8":

            if weather_code in SNOW_CODES:

                reasons.append(
                    "Snowy weather"
                )

            elif temperature <= 5:

                reasons.append(
                    "Very cold weather"
                )

            elif temperature <= 10:

                reasons.append(
                    "Cold winter weather"
                )

    return reasons


# ============================================================
# FIND BEST DESTINATIONS
# ============================================================

def find_best_destinations(
    weather_data,
    selected_interests,
):

    matches = []

    for weather in weather_data:

        score = calculate_score(
            weather,
            selected_interests,
        )

        if score <= 0:
            continue

        reasons = get_match_reason(
            weather,
            selected_interests,
        )

        weather["score"] = score

        weather["reasons"] = reasons

        matches.append(weather)

    matches.sort(
        key=lambda destination:
        destination["score"],
        reverse=True,
    )

    return matches


# ============================================================
# SHOW BEST RECOMMENDATION
# ============================================================

def show_recommendation(destination):

    print()

    print(
        GREEN
        + "╔══════════════════════════════════════════════╗"
        + RESET
    )

    print(
        GREEN
        + "║              🏆 YOUR BEST MATCH             ║"
        + RESET
    )

    print(
        GREEN
        + "╚══════════════════════════════════════════════╝"
        + RESET
    )

    print()

    print(
        CYAN
        + f"🌍 {destination['flag']} "
        + destination["country"]
        + RESET
    )

    print(
        YELLOW
        + f"📍 {destination['city']}"
        + RESET
    )

    print()

    print(
        MAGENTA
        + f"📊 Match Score: {destination['score']}"
        + RESET
    )

    print(
        f"🌡️ Temperature: "
        f"{destination['temperature']}°C"
    )

    print(
        f"💧 Humidity: "
        f"{destination['humidity']}%"
    )

    print()

    print(
        BLUE
        + "💡 Why this destination?"
        + RESET
    )

    if destination["reasons"]:

        for reason in destination["reasons"]:

            print(
                f"   ✅ {reason}"
            )

    print()

    print(
        GREEN
        + "✨ This destination matches your preferences!"
        + RESET
    )


# ============================================================
# SHOW OTHER MATCHES
# ============================================================

def show_other_matches(matches):

    if len(matches) <= 1:
        return

    print()

    print(
        CYAN
        + "🌎 OTHER GOOD MATCHES"
        + RESET
    )

    print()

    for number, destination in enumerate(
        matches[1:4],
        start=2,
    ):

        print(
            f"  {YELLOW}{number}{RESET}. "
            f"{destination['flag']} "
            f"{destination['city']}, "
            f"{destination['country']}"
            f"  —  ⭐ {destination['score']}"
        )


# ============================================================
# MAIN RECOMMENDATION FEATURE
# ============================================================

def find_my_destination():

    selected_interests = choose_interests()

    if selected_interests is None:
      return

    print()

    print(
        CYAN
        + "🤖 Analyzing destinations"
        + RESET,
        end="",
    )

    for _ in range(3):

        time.sleep(0.3)

        print(
            ".",
            end="",
            flush=True,
        )

    print()

    print()

    print(
        YELLOW
        + "🌤️ Checking live weather data..."
        + RESET
    )

    cities = get_all_cities()

    weather_data = get_live_weather(
        cities
    )

    if not weather_data:

        print()

        print(
            RED
            + "❌ Could not retrieve live weather data."
            + RESET
        )

        print(
            WHITE
            + "Please check your internet connection and try again."
            + RESET
        )

        return

    print(
        GREEN
        + f"✓ Weather data received for "
        f"{len(weather_data)} cities."
        + RESET
    )

    print()

    matches = find_best_destinations(
        weather_data,
        selected_interests,
    )

    if not matches:

        print(
            RED
            + "❌ No suitable destination found."
            + RESET
        )

        print()

        print(
            YELLOW
            + "💡 Try another combination of interests."
            + RESET
        )

        return

    best_destination = matches[0]

    show_recommendation(
        best_destination
    )

    show_other_matches(
        matches
    )