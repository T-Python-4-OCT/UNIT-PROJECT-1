from agency.config import GROUP_DISCOUNT_PERCENT, GROUP_SIZE
from agency.errors import ServiceError
from agency.models.country import Country
from agency.services import countries


STYLES = {"economy": 0.7, "standard": 1.0, "luxury": 1.8}
BASE_ITEMS = ("Flights", "Hotel", "Food", "Transport", "Activities")


def estimate(destination: Country, days: int, travelers: int, style: str) -> dict:
    if days < 2:
        raise ServiceError("A trip needs at least 2 days.")
    if travelers < 1:
        raise ServiceError("At least 1 traveler is required.")
    if style not in STYLES:
        raise ServiceError(f"Style must be one of: {', '.join(STYLES)}.")

    multiplier = STYLES[style]
    nights = days - 1
    breakdown = {
        "Flights": destination.flight * travelers,
        "Hotel": round(destination.hotel * multiplier * nights * travelers),
        "Food": round(destination.food * multiplier * days * travelers),
        "Transport": round(destination.transport * days * travelers),
        "Activities": round(destination.activities * multiplier * days * travelers),
    }
    if travelers == GROUP_SIZE:
        breakdown[f"Group discount ({GROUP_DISCOUNT_PERCENT}%)"] = -round(
            sum(breakdown.values()) * GROUP_DISCOUNT_PERCENT / 100)
    breakdown["Total"] = sum(breakdown.values())
    return breakdown


def apply_promo(breakdown: dict, code: str, percent: int) -> dict:
    base = sum(breakdown[item] for item in BASE_ITEMS)
    result = {item: value for item, value in breakdown.items() if item != "Total"}
    result[f"Code {code} ({percent}%)"] = -round(base * percent / 100)
    result["Total"] = sum(result.values())
    return result


def find_matches(budget: int, days: int, travelers: int, style: str,
                 category: str = "", limit: int = 10):
    if budget <= 0:
        raise ServiceError("Budget must be greater than zero.")
    options = [(destination, estimate(destination, days, travelers, style))
               for destination in countries.search(category=category) if not destination.suspended]
    if not options:
        raise ServiceError("No destinations found for this filter.")
    affordable = [o for o in options if o[1]["Total"] <= budget]
    affordable.sort(key=lambda o: o[1]["Total"], reverse=True)
    cheapest = min(options, key=lambda o: o[1]["Total"])
    return affordable[:limit], cheapest


def build_itinerary(destination: Country, days: int) -> list:
    if days < 2:
        raise ServiceError("A trip needs at least 2 days.")
    plan = [f"Arrive in {destination.city}, check in and relax"]
    for i in range(days - 2):
        plan.append(destination.highlights[i % len(destination.highlights)])
    plan.append("Last-minute shopping and departure")
    return plan
