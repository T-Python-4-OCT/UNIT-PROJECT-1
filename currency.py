import requests


CURRENCY_CODES = {
    "Saudi Arabia": "SAR",
    "United Arab Emirates": "AED",
    "Kuwait": "KWD",
    "Qatar": "QAR",
    "Japan": "JPY",
    "China": "CNY",
    "South Korea": "KRW",
    "India": "INR",
    "Thailand": "THB",
    "Malaysia": "MYR",
    "Indonesia": "IDR",
    "United Kingdom": "GBP",
    "France": "EUR",
    "Germany": "EUR",
    "Italy": "EUR",
    "Spain": "EUR",
    "Turkey": "TRY",
    "Switzerland": "CHF",
    "Netherlands": "EUR",
    "Egypt": "EGP",
    "Morocco": "MAD",
    "South Africa": "ZAR",
    "Kenya": "KES",
    "Tanzania": "TZS",
    "United States": "USD",
    "Canada": "CAD",
    "Mexico": "MXN",
    "Brazil": "BRL",
    "Argentina": "ARS",
    "Australia": "AUD",
    "New Zealand": "NZD",
    "Fiji": "FJD",
}


CURRENCY_NAMES = {
    "SAR": "Saudi Riyal",
    "AED": "UAE Dirham",
    "KWD": "Kuwaiti Dinar",
    "QAR": "Qatari Riyal",
    "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan",
    "KRW": "South Korean Won",
    "INR": "Indian Rupee",
    "THB": "Thai Baht",
    "MYR": "Malaysian Ringgit",
    "IDR": "Indonesian Rupiah",
    "GBP": "British Pound",
    "EUR": "Euro",
    "TRY": "Turkish Lira",
    "CHF": "Swiss Franc",
    "EGP": "Egyptian Pound",
    "MAD": "Moroccan Dirham",
    "ZAR": "South African Rand",
    "KES": "Kenyan Shilling",
    "TZS": "Tanzanian Shilling",
    "USD": "US Dollar",
    "CAD": "Canadian Dollar",
    "MXN": "Mexican Peso",
    "BRL": "Brazilian Real",
    "ARS": "Argentine Peso",
    "AUD": "Australian Dollar",
    "NZD": "New Zealand Dollar",
    "FJD": "Fijian Dollar",
}


def get_currency_code(country_name):
    return CURRENCY_CODES.get(country_name)


def get_currency_rate(from_currency, to_currency="SAR"):
    if from_currency == to_currency:
        return 1.0

    url = f"https://open.er-api.com/v6/latest/{from_currency}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        rates = data.get("rates", {})

        return rates.get(to_currency)

    except requests.RequestException:
        return None


def convert_currency(amount, from_currency, to_currency="SAR"):
    rate = get_currency_rate(
        from_currency,
        to_currency,
    )

    if rate is None:
        return None

    return amount * rate


def show_currency(country_name):
    print("\n" + "=" * 50)
    print(f"💰 Currency - {country_name}")
    print("=" * 50)

    currency_code = get_currency_code(country_name)

    if not currency_code:
        print("❌ Currency information is unavailable.")
        return

    currency_name = CURRENCY_NAMES.get(
        currency_code,
        currency_code,
    )

    print(f"\nCurrency: {currency_name}")
    print(f"Code: {currency_code}")

    if currency_code != "SAR":
        rate = get_currency_rate(currency_code, "SAR")

        if rate is not None:
            print(f"1 {currency_code} ≈ {rate:.4f} SAR")
        else:
            print("⚠️ Live exchange rate is unavailable.")