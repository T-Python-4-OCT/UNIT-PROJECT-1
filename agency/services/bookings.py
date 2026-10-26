import secrets
from datetime import datetime

from agency.config import BOOKINGS_FILE
from agency.errors import ServiceError
from agency.models.booking import Booking
from agency.services import countries, planner, promos
from agency.storage import json_db
from agency.utils import validators

STATUSES = ("pending", "confirmed", "completed", "cancelled")
ACTIVE_STATUSES = ("pending", "confirmed")
PAYMENT_METHODS = ("card", "apple_pay")


# تقرأ كل الحجوزات من الملف وترجعها ككائنات Booking.
def _load() -> list:
    return [Booking.from_dict(record) for record in json_db.load(BOOKINGS_FILE)]


# تحفظ قائمة الحجوزات في الملف.
def _save(bookings: list) -> None:
    json_db.save(BOOKINGS_FILE, [booking.to_dict() for booking in bookings])


# تدور على حجز بالرقم أو ترمي ServiceError.
def _find(bookings: list, booking_id: int, user_id=None) -> Booking:
    for booking in bookings:
        if booking.id == booking_id and (user_id is None or booking.user_id == user_id):
            return booking
    raise ServiceError(f"Booking #{booking_id} not found.")


# ترجع كل الحجوزات.
def list_all() -> list:
    return _load()


# ترجع حجوزات عميل واحد.
def list_for_user(user_id: int) -> list:
    return [booking for booking in _load() if booking.user_id == user_id]


# ترجع حجز واحد بالرقم (وتتأكد أنه للعميل إذا انحدد).
def get(booking_id: int, user_id=None) -> Booking:
    return _find(_load(), booking_id, user_id)


# تنشئ حجز جديد بسعره (مع الخصومات) وحالته معلق.
def create(user_id: int, country_id: int, travel_date: str, days: int,
           travelers: int, style: str, promo_code: str = "") -> Booking:
    travel_date = validators.parse_future_date(travel_date)
    country = countries.get(country_id)
    if country.suspended:
        raise ServiceError(f"{country.city} is suspended until further notice and cannot be booked.")
    cost = planner.estimate(country, days, travelers, style)
    promo_code = promos.normalize(promo_code)
    if promo_code:
        promo = promos.get_active(promo_code)
        cost = planner.apply_promo(cost, promo.code, promo.percent)
    bookings = _load()
    booking = Booking(
        id=max((booking.id for booking in bookings), default=0) + 1,
        user_id=user_id, country_id=country.id, country=country.country,
        city=country.city, travel_date=travel_date, days=days,
        travelers=travelers, style=style, total_price=cost["Total"],
        breakdown=cost, status="pending", promo_code=promo_code,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )
    bookings.append(booking)
    _save(bookings)
    return booking


# تلغي الحجز وترجع مبلغ الاسترجاع (كامل السعر إذا كان مدفوع، وإلا صفر).
def _cancel(booking: Booking) -> int:
    refund = booking.total_price if booking.paid else 0
    booking.status = "cancelled"
    booking.paid = False
    return refund


# العميل يلغي حجزه، وترجع المبلغ المسترجع.
def cancel(booking_id: int, user_id: int):
    bookings = _load()
    booking = _find(bookings, booking_id, user_id)
    if booking.status not in ACTIVE_STATUSES:
        raise ServiceError("Only pending or confirmed bookings can be cancelled.")
    refund = _cancel(booking)
    _save(bookings)
    return booking, refund


# تلغي كل حجوزات العميل النشطة (عند حذفه).
def cancel_active_for_user(user_id: int) -> list:
    all_bookings = _load()
    results = [(booking, _cancel(booking)) for booking in all_bookings
               if booking.user_id == user_id and booking.status in ACTIVE_STATUSES]
    if results:
        _save(all_bookings)
    return results


# تتحقق من بيانات الدفع وتسجله وتنشئ رقم مرجعي (البطاقة ما تنحفظ).
def pay(booking_id: int, user_id: int, method: str, card_number: str = "",
        card_holder: str = "", cvv: str = "") -> Booking:
    if method not in PAYMENT_METHODS:
        raise ServiceError(f"Payment method must be one of: {', '.join(PAYMENT_METHODS)}.")
    bookings = _load()
    booking = _find(bookings, booking_id, user_id)
    if booking.status == "cancelled":
        raise ServiceError("This booking was cancelled.")
    if booking.paid:
        raise ServiceError("This booking is already paid.")
    if method == "card":
        if not validators.is_valid_card_holder(card_holder):
            raise ServiceError("Name on card is not valid (letters only, at least 3).")
        if not validators.is_valid_card_number(card_number):
            raise ServiceError("Card number must be 8 to 16 digits.")
        if not validators.is_valid_cvv(cvv):
            raise ServiceError("CVV must be 3 or 4 digits.")

    booking.paid = True
    booking.status = "confirmed"
    booking.payment_method = method
    booking.reference = f"SR-{booking.id:04d}-{secrets.token_hex(2).upper()}"
    _save(bookings)
    return booking


# المدير يغيّر حالة الحجز، والإلغاء يرجّع المبلغ.
def set_status(booking_id: int, new_status: str):
    if new_status not in STATUSES:
        raise ServiceError(f"Status must be one of: {', '.join(STATUSES)}.")
    bookings = _load()
    booking = _find(bookings, booking_id)
    if booking.status == "cancelled":
        raise ServiceError("Cancelled bookings cannot be changed.")
    if new_status in ("confirmed", "completed") and not booking.paid:
        raise ServiceError("Only paid bookings can be confirmed or completed.")
    refund = 0
    if new_status == "cancelled":
        refund = _cancel(booking)
    else:
        booking.status = new_status
    _save(bookings)
    return booking, refund


# ترجع الحجز المدفوع عشان يطلع إيصاله، وترمي ServiceError إذا ما اندفع.
def receipt(booking_id: int, user_id: int) -> Booking:
    booking = get(booking_id, user_id)
    if not booking.paid:
        raise ServiceError("No receipt yet: this booking has not been paid.")
    return booking
