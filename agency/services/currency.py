"""Local currency of each destination and an approximate exchange rate from the Saudi riyal."""
from agency.config import CURRENCY

SAR_PER_USD = 3.75          # the riyal is pegged to the dollar

# country name -> (currency name, code, units of that currency per 1 USD). Rough values, not live.
LOCAL_CURRENCIES = {
    "Turkey": ("Turkish lira", "TRY", 41.0),
    "UAE": ("UAE dirham", "AED", 3.67),
    "Egypt": ("Egyptian pound", "EGP", 48.0),
    "Jordan": ("Jordanian dinar", "JOD", 0.71),
    "France": ("Euro", "EUR", 0.86),
    "United Kingdom": ("Pound sterling", "GBP", 0.75),
    "Italy": ("Euro", "EUR", 0.86),
    "Spain": ("Euro", "EUR", 0.86),
    "Switzerland": ("Swiss franc", "CHF", 0.80),
    "Japan": ("Japanese yen", "JPY", 150.0),
    "Thailand": ("Thai baht", "THB", 33.0),
    "Malaysia": ("Malaysian ringgit", "MYR", 4.2),
    "Indonesia": ("Indonesian rupiah", "IDR", 16500.0),
    "Maldives": ("Maldivian rufiyaa", "MVR", 15.4),
    "Morocco": ("Moroccan dirham", "MAD", 9.2),
    "Georgia": ("Georgian lari", "GEL", 2.7),
    "USA": ("US dollar", "USD", 1.0),
    "South Korea": ("South Korean won", "KRW", 1400.0),
    "Greece": ("Euro", "EUR", 0.86),
    "Azerbaijan": ("Azerbaijani manat", "AZN", 1.7),
    "Oman": ("Omani rial", "OMR", 0.385),
    "Bosnia": ("Convertible mark", "BAM", 1.68),
    "Austria": ("Euro", "EUR", 0.86),
    "Netherlands": ("Euro", "EUR", 0.86),
    "Germany": ("Euro", "EUR", 0.86),
    "Singapore": ("Singapore dollar", "SGD", 1.3),
    "China": ("Chinese yuan", "CNY", 7.1),
    "Portugal": ("Euro", "EUR", 0.86),
}


# ترجع عملة الدولة وسعر الصرف التقريبي مقابل الريال، أو None إذا الدولة غير معروفة.
def local_currency(country: str):
    """(currency name, code, how many units of it equal 1 SAR), or None for an unknown country."""
    entry = LOCAL_CURRENCIES.get(country)
    if entry is None:
        return None
    name, code, per_usd = entry
    return name, code, per_usd / SAR_PER_USD


# تحوّل مبلغ بالريال إلى عملة الدولة.
def convert(amount_sar: float, rate: float) -> float:
    """An amount in riyals expressed in the local currency."""
    return amount_sar * rate


# تنسّق الرقم عشان يقرأ بسهولة (بدون كسور للكبير، وكسور للصغير).
def format_amount(value: float) -> str:
    """Readable number: no decimals for big values (yen, rupiah), more decimals for small ones."""
    if value >= 100:
        return f"{value:,.0f}"
    return f"{value:,.2f}" if value >= 1 else f"{value:,.4f}"


# ترجع سطرين للإيصال: سعر الصرف والمجموع بعملة الدولة.
def describe(country: str, total_sar: float):
    """Two receipt lines (rate, total in local currency), or None when the country is unknown."""
    found = local_currency(country)
    if found is None:
        return None
    name, code, rate = found
    return (f"{name} ({code}): 1 {CURRENCY} = {format_amount(rate)} {code} (approx.)",
            f"Your total is about {format_amount(convert(total_sar, rate))} {code}")
