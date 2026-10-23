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


def remove_duplicate_holidays(holiday_list):
    unique = []
    seen = set()

    for holiday_date, holiday_name in holiday_list:
        key = (
            holiday_date,
            holiday_name.lower().strip(),
        )

        if key not in seen:
            seen.add(key)
            unique.append(
                (holiday_date, holiday_name)
            )

    return unique


def get_holidays(country_name, year=2026):
    country_code = COUNTRY_CODES.get(country_name)

    if not country_code:
        return []

    try:
        country_holidays = holidays.country_holidays(
            country_code,
            years=year,
        )
    except Exception:
        return []

    holiday_list = []

    for holiday_date, holiday_name in country_holidays.items():
        holiday_list.append(
            (
                holiday_date,
                holiday_name,
            )
        )

    holiday_list.sort(key=lambda item: item[0])

    return remove_duplicate_holidays(holiday_list)


def show_holidays(country_name, year=2026):
    print("\n" + "=" * 50)
    print(f"🎉 Holidays - {country_name}")
    print("=" * 50)

    holiday_list = get_holidays(
        country_name,
        year,
    )

    if not holiday_list:
        print("❌ No holiday information available.")
        return

    for holiday_date, holiday_name in holiday_list:
        formatted_date = holiday_date.strftime("%d %B %Y")

        print(
            f"📅 {formatted_date} - {holiday_name}"
        )