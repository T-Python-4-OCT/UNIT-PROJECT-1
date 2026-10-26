from collections import Counter

from agency.config import DEFAULT_DAYS
from agency.services import bookings, countries, planner


# تحسب تكلفة مرجعية للوجهة (7 أيام لمسافر واحد) لترتيب التوصيات.
def _reference_cost(destination) -> int:
    return planner.estimate(destination, DEFAULT_DAYS, 1, "standard")["Total"]


# ترشح وجهات للعميل (الأشهر أو حسب ذوقه)، بدون اللي حجزها أو الموقوفة.
def recommend(user_id: int, limit: int = 3, category: str = "") -> list:
    catalog = countries.list_all()
    by_id = {destination.id: destination for destination in catalog}
    active = [booking for booking in bookings.list_all() if booking.status != "cancelled"]
    popularity = Counter(booking.country_id for booking in active)

    mine = [booking for booking in active if booking.user_id == user_id and booking.country_id in by_id]
    booked_ids = {booking.country_id for booking in mine}
    candidates = [destination for destination in catalog
                  if destination.id not in booked_ids and not destination.suspended
                  and (not category or destination.category == category)]


    if not mine:
        ranked = sorted(candidates, key=lambda destination: (-popularity[destination.id], _reference_cost(destination)))
        return [(destination, "Popular with our travelers" if popularity[destination.id]
                 else "A great-value trip to start with") for destination in ranked[:limit]]

    favourite = Counter(by_id[booking.country_id].category for booking in mine).most_common(1)[0][0]
    avg_cost = sum(_reference_cost(by_id[booking.country_id]) for booking in mine) / len(mine)

    scored = []
    for destination in candidates:
        score, reasons = 0.0, []
        if not category and destination.category == favourite:
            score += 3
            reasons.append(f"You enjoy {favourite} trips")
        cost = _reference_cost(destination)
        if abs(cost - avg_cost) <= 0.3 * avg_cost:
            score += 2
            reasons.append("Similar budget to your past trips")
        if popularity[destination.id]:
            score += min(popularity[destination.id], 3) * 0.5
            reasons.append("Popular with our travelers")
        scored.append((score, cost, destination, reasons))

    scored.sort(key=lambda t: (-t[0], t[1]))
    return [(destination, " + ".join(reasons) or "Something new to explore")
            for _, _, destination, reasons in scored[:limit]]
