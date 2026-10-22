
COUNTRY_CODES = {
    "austria": "AT", "azerbaijan": "AZ", "bosnia": "BA", "china": "CN", "egypt": "EG",
    "france": "FR", "georgia": "GE", "germany": "DE", "greece": "GR", "indonesia": "ID",
    "italy": "IT", "japan": "JP", "jordan": "JO", "malaysia": "MY", "maldives": "MV",
    "morocco": "MA", "netherlands": "NL", "oman": "OM", "portugal": "PT", "singapore": "SG",
    "south korea": "KR", "spain": "ES", "switzerland": "CH", "thailand": "TH", "turkey": "TR",
    "uae": "AE", "usa": "US", "united kingdom": "GB",
}
UNKNOWN_FLAG = "🌍"
_FIRST_LETTER = 0x1F1E6


def flag(country: str) -> str:
    code = COUNTRY_CODES.get(country.strip().lower())
    if not code:
        return UNKNOWN_FLAG
    return "".join(chr(_FIRST_LETTER + ord(letter) - ord("A")) for letter in code)
