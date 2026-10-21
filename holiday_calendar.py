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
    "Fiji": "FJ"
}


WEEKENDS = {
    "Saudi Arabia": ["Friday", "Saturday"],
    "United Arab Emirates": ["Saturday", "Sunday"],
    "Kuwait": ["Friday", "Saturday"],
    "Qatar": ["Friday", "Saturday"],
    "Egypt": ["Friday", "Saturday"]
}


def get_holidays(country_name, year=None):
    if country_name not in COUNTRY_CODES:
        return []

    if year is None:
        year = date.today().year

    country_code = COUNTRY_CODES[country_name]

    try:
        country_holidays = holidays.country_holidays(
            country_code,
            years=year
        )

        return [
            {
                "date": holiday_date,
                "name": holiday_name
            }
            for holiday_date, holiday_name
            in sorted(country_holidays.items())
        ]

    except Exception as error:
        print(f"❌ Holiday API error: {error}")
        return []


def get_weekend(country_name):
    return WEEKENDS.get(
        country_name,
        ["Saturday", "Sunday"]
    )


def show_holidays(country_name, year=None):
    holiday_list = get_holidays(
        country_name,
        year
    )

    weekend = get_weekend(country_name)

    print()
    print("📅 Travel Calendar")
    print()
    print(
        f"🗓️ Weekly Weekend: "
        f"{' & '.join(weekend)}"
    )

    print()
    print("🎉 Official Holidays:")

    if not holiday_list:
        print("❌ No holiday information available.")
        return

    grouped_holidays = {}

    for holiday in holiday_list:
        holiday_name = holiday["name"].replace(
            " (observed)",
            ""
        )

        if holiday_name not in grouped_holidays:
            grouped_holidays[holiday_name] = []

        grouped_holidays[holiday_name].append(
            holiday["date"]
        )

    for holiday_name, dates in grouped_holidays.items():

        if len(dates) == 1:
            print(
                f"📌 {dates[0]} - "
                f"{holiday_name}"
            )

        else:
            print(
                f"📌 {dates[0]} → {dates[-1]} - "
                f"{holiday_name}"
            )
