CURRENCIES = {
    "Saudi Arabia": {
        "name": "Saudi Riyal",
        "code": "SAR"
    },
    "United Arab Emirates": {
        "name": "UAE Dirham",
        "code": "AED"
    },
    "Kuwait": {
        "name": "Kuwaiti Dinar",
        "code": "KWD"
    },
    "Qatar": {
        "name": "Qatari Riyal",
        "code": "QAR"
    },
    "Japan": {
        "name": "Japanese Yen",
        "code": "JPY"
    },
    "China": {
        "name": "Chinese Yuan",
        "code": "CNY"
    },
    "South Korea": {
        "name": "South Korean Won",
        "code": "KRW"
    },
    "India": {
        "name": "Indian Rupee",
        "code": "INR"
    },
    "Thailand": {
        "name": "Thai Baht",
        "code": "THB"
    },
    "Malaysia": {
        "name": "Malaysian Ringgit",
        "code": "MYR"
    },
    "Indonesia": {
        "name": "Indonesian Rupiah",
        "code": "IDR"
    },
    "United Kingdom": {
        "name": "British Pound",
        "code": "GBP"
    },
    "France": {
        "name": "Euro",
        "code": "EUR"
    },
    "Germany": {
        "name": "Euro",
        "code": "EUR"
    },
    "Italy": {
        "name": "Euro",
        "code": "EUR"
    },
    "Spain": {
        "name": "Euro",
        "code": "EUR"
    },
    "Turkey": {
        "name": "Turkish Lira",
        "code": "TRY"
    },
    "Switzerland": {
        "name": "Swiss Franc",
        "code": "CHF"
    },
    "Netherlands": {
        "name": "Euro",
        "code": "EUR"
    },
    "Egypt": {
        "name": "Egyptian Pound",
        "code": "EGP"
    },
    "Morocco": {
        "name": "Moroccan Dirham",
        "code": "MAD"
    },
    "South Africa": {
        "name": "South African Rand",
        "code": "ZAR"
    },
    "Kenya": {
        "name": "Kenyan Shilling",
        "code": "KES"
    },
    "Tanzania": {
        "name": "Tanzanian Shilling",
        "code": "TZS"
    },
    "United States": {
        "name": "US Dollar",
        "code": "USD"
    },
    "Canada": {
        "name": "Canadian Dollar",
        "code": "CAD"
    },
    "Mexico": {
        "name": "Mexican Peso",
        "code": "MXN"
    },
    "Brazil": {
        "name": "Brazilian Real",
        "code": "BRL"
    },
    "Argentina": {
        "name": "Argentine Peso",
        "code": "ARS"
    },
    "Australia": {
        "name": "Australian Dollar",
        "code": "AUD"
    },
    "New Zealand": {
        "name": "New Zealand Dollar",
        "code": "NZD"
    },
    "Fiji": {
        "name": "Fijian Dollar",
        "code": "FJD"
    }
}


def get_currency(country_name):
    return CURRENCIES.get(country_name)
