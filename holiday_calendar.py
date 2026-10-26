
from datetime import date

import holidays


COUNTRY_CODES = {
    "Saudi Arabia": "SA",
    "United Arab Emirates": "AE",
    "Kuwait": "KW",
    "Qatar": "QA",
    "Japan": "JP",
    "China": "CN",
    "South Korea": "KR",
    "India": "IN",
    "Thailand": "TH",
    "Malaysia": "MY",
    "Indonesia": "ID",
    "United Kingdom": "GB",
    "France": "FR",
    "Germany": "DE",
    "Italy": "IT",
    "Spain": "ES",
    "Turkey": "TR",
    "Switzerland": "CH",
    "Netherlands": "NL",
    "Egypt": "EG",
    "Morocco": "MA",
    "South Africa": "ZA",
    "Kenya": "KE",
    "Tanzania": "TZ",
    "United States": "US",
    "Canada": "CA",
    "Mexico": "MX",
    "Brazil": "BR",
    "Argentina": "AR",
    "Australia": "AU",
    "New Zealand": "NZ",
    "Fiji": "FJ",
}
WEEKENDS = {
    "Saudi Arabia": ["Friday", "Saturday"],
    "United Arab Emirates": ["Saturday", "Sunday"],
    "Kuwait": ["Friday", "Saturday"],
    "Qatar": ["Friday", "Saturday"],
    "Japan": ["Saturday", "Sunday"],
    "China": ["Saturday", "Sunday"],
    "South Korea": ["Saturday", "Sunday"],
    "India": ["Saturday", "Sunday"],
    "Thailand": ["Saturday", "Sunday"],
    "Malaysia": ["Saturday", "Sunday"],
    "Indonesia": ["Saturday", "Sunday"],
    "United Kingdom": ["Saturday", "Sunday"],
    "France": ["Saturday", "Sunday"],
    "Germany": ["Saturday", "Sunday"],
    "Italy": ["Saturday", "Sunday"],
    "Spain": ["Saturday", "Sunday"],
    "Turkey": ["Saturday", "Sunday"],
    "Switzerland": ["Saturday", "Sunday"],
    "Netherlands": ["Saturday", "Sunday"],
    "Egypt": ["Friday", "Saturday"],
    "Morocco": ["Saturday", "Sunday"],
    "South Africa": ["Saturday", "Sunday"],
    "Kenya": ["Saturday", "Sunday"],
    "Tanzania": ["Saturday", "Sunday"],
    "United States": ["Saturday", "Sunday"],
    "Canada": ["Saturday", "Sunday"],
    "Mexico": ["Saturday", "Sunday"],
    "Brazil": ["Saturday", "Sunday"],
    "Argentina": ["Saturday", "Sunday"],
    "Australia": ["Saturday", "Sunday"],
    "New Zealand": ["Saturday", "Sunday"],
    "Fiji": ["Saturday", "Sunday"],
}


def get_holidays(country_name, year=2026):
    country_code = COUNTRY_CODES.get(country_name)

    if not country_code:
        return []

    try:
        country_holidays = holidays.country_holidays(
            country_code,
            years=year,
            language="en_US",
        )
    except Exception:
        return []

    holiday_list = []

    for holiday_date, holiday_name in country_holidays.items():
        holiday_list.append(
            (
                holiday_date,
                holiday_name.strip(),
            )
        )

    holiday_list.sort(key=lambda item: item[0])

    return holiday_list

def get_weekend(country_name):
    return WEEKENDS[country_name]


def group_holidays(holiday_list):
    grouped = []

    for holiday_date, holiday_name in holiday_list:
        if not grouped:
            grouped.append(
                {
                    "name": holiday_name,
                    "start": holiday_date,
                    "end": holiday_date,
                }
            )
            continue

        previous = grouped[-1]

        if (
            holiday_name.lower() == previous["name"].lower()
            and (holiday_date - previous["end"]).days == 1
        ):
            previous["end"] = holiday_date
        else:
            grouped.append(
                {
                    "name": holiday_name,
                    "start": holiday_date,
                    "end": holiday_date,
                }
            )

    return grouped


def show_holidays(country_name, year=2026):
    print("\n" + "=" * 50)
    print(f"🎉 Holidays - {country_name}")
    print("=" * 50)

    weekend = get_weekend(country_name)

    print("┌─────────────────────────────────────┐")
    print("│  🗓️  Weekly Weekend                 │")
    print(f"│   {weekend[0]} & {weekend[1]}                 │")
    print("└─────────────────────────────────────┘")
    print()

    
    print("┌──────────────────────────────────────────────┐")
    print("│ 🎉  OFFICIAL HOLIDAYS & OCCASIONS            │")
    print("└──────────────────────────────────────────────┘")
    print()

    holiday_list = get_holidays(
        country_name,
        year,
    )
    
    if not holiday_list:
        print("❌ No holiday information available.")
        return

    grouped_holidays = group_holidays(holiday_list)

    for holiday in grouped_holidays:
        start_date = holiday["start"].strftime("%d %B %Y")
        end_date = holiday["end"].strftime("%d %B %Y")

        if holiday["start"] == holiday["end"]:
            print(
                f"📅 {start_date} - {holiday['name']}"
            )
        else:
            print(
                f"📅 {start_date} - {end_date} - "
                f"{holiday['name']}"
            )
