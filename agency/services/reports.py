from collections import Counter
from datetime import date

from agency.config import USERS_FILE
from agency.services import bookings, countries
from agency.storage import json_db


# ملاحظات الترحيب: للمدير حجوزات تنتظر، وللعميل حجوزات غير مدفوعة ورحلته القادمة.
def welcome_notes(user) -> list:
    if user.role == "manager":
        waiting = sum(booking.status == "confirmed" for booking in bookings.list_all())
        paused = sum(destination.suspended for destination in countries.list_all())
        notes = [f"{waiting} confirmed booking(s) waiting to be completed."]
        if paused:
            notes.append(f"{paused} trip(s) are suspended until further notice.")
        return notes

    mine = bookings.list_for_user(user.id)
    unpaid = sum(booking.status == "pending" for booking in mine)
    upcoming = sorted(booking.travel_date for booking in mine
                      if booking.status == "confirmed" and booking.travel_date >= date.today().isoformat())
    notes = []
    if unpaid:
        notes.append(f"You have {unpaid} unpaid booking(s).")
    if upcoming:
        notes.append(f"Your next trip starts on {upcoming[0]}.")
    if not mine:
        notes.append("No bookings yet. Try 'Plan a trip by budget' to get started.")
    return notes


# تحسب تقرير الوكالة: الإيرادات والحجوزات وأكثر الوجهات.
def summary() -> dict:
    all_bookings = bookings.list_all()
    paid = [booking for booking in all_bookings if booking.paid]
    revenue = sum(booking.total_price for booking in paid)

    by_status = {s: 0 for s in bookings.STATUSES}
    by_status.update(Counter(booking.status for booking in all_bookings))

    by_destination = {}
    for booking in all_bookings:
        if booking.status == "cancelled":
            continue
        key = f"{booking.city}, {booking.country}"
        count, money = by_destination.get(key, (0, 0))
        by_destination[key] = (count + 1, money + (booking.total_price if booking.paid else 0))
    top = sorted(by_destination.items(), key=lambda kv: (-kv[1][0], -kv[1][1]))[:5]

    customers = sum(1 for user_record in json_db.load(USERS_FILE) if user_record["role"] == "customer")
    return {
        "total_bookings": len(all_bookings),
        "revenue": revenue,
        "average_booking": round(revenue / len(paid)) if paid else 0,
        "customers": customers,
        "by_status": by_status,
        "top_destinations": top,
    }
