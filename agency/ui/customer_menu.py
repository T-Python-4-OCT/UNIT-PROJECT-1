
from agency.config import (CURRENCY, DEFAULT_DAYS, GROUP_DISCOUNT_PERCENT, GROUP_SIZE,
                           MAX_DAYS, MIN_DAYS, REFUND_NOTICE)
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import bookings, countries, notifications, planner, promos, weather
from agency.ui import views
from agency.ui.console import (GoBack, ask_choice, ask_int, ask_text, confirm, console, error,
                               info, pause, success, warn)
from agency.utils import validators

MENU = [
    ("1", "Browse destinations"),
    ("2", "View destination details + live weather"),
    ("3", "Search destinations"),
    ("4", "Plan a trip by budget"),
    ("5", "Book a trip"),
    ("6", "My bookings"),
    ("7", "Pay for a booking"),
    ("8", "Cancel a booking"),
    ("9", "View receipt"),
    ("0", "Logout"),
]


# حلقة قائمة العميل لين يختار الخروج.
def run(user: User) -> None:
    actions = {
        "1": browse,
        "2": details,
        "3": search,
        "4": lambda: plan_trip(user),
        "5": lambda: book_trip(user),
        "6": lambda: my_bookings(user),
        "7": lambda: pay(user),
        "8": lambda: cancel(user),
        "9": lambda: receipt(user),
    }
    while True:
        console.print()
        views.show_menu(f"Customer menu - {user.full_name}", MENU)
        choice = ask_choice("Choose", [k for k, _ in MENU], allow_back=False)
        if choice == "0":
            info("Logged out. See you soon!")
            return
        try:
            actions[choice]()
        except GoBack:
            info("Cancelled. Back to the menu.")
            continue
        except ServiceError as exc:
            error(str(exc))
        pause()


# تعرض كل الوجهات في جدول.
def browse() -> None:
    views.show_countries(countries.list_all(), "All destinations")


# تعرض الوجهات ثم تسأل عن رقم وجهة وتعرض تفاصيلها مع الطقس.
def details() -> None:
    browse()
    _show_destination_report(countries.get(ask_int("Destination ID", minimum=1)))


# تعرض تفاصيل الوجهة ثم الطقس الحي.
def _show_destination_report(destination) -> None:
    views.show_country_detail(destination)
    _show_live_weather(destination)


# تجيب الطقس وتعرضه، وإذا فشل (ما فيه إنترنت) تعرض تنبيه أصفر وتكمل.
def _show_live_weather(destination) -> None:
    try:
        with console.status("[cyan]Fetching live weather...[/cyan]"):
            report = weather.get_forecast(destination)
    except ServiceError as exc:
        warn(str(exc))
        return
    views.show_weather(report)


# تبحث في الوجهات بالدولة أو المدينة أو النوع (مع تصحيح الإملاء).
def search() -> None:
    field = ask_choice("Search by", ["country", "city", "type"])
    if field == "type":
        query = ask_choice("Trip type", countries.CATEGORIES)
        results, corrected = countries.search_by("category", query)
    else:
        query = ask_text(f"Enter the {field} name")
        results, corrected = countries.search_by(field, query)
    if not results:
        warn(f"No destinations match '{query}'.")
        return
    if corrected:
        warn(f"No exact match for '{query}'. Showing the closest spelling instead.")
    views.show_countries(results, f"Results for '{query}'")
    _offer_details(results)


# تسأل عن رقم من نتائج البحث وتعرض تفاصيله مع الطقس.
def _offer_details(results) -> None:
    listed_ids = {destination.id for destination in results}
    while True:
        chosen = ask_int("Enter an ID to see its details and live weather (0 to skip)", minimum=0)
        if chosen == 0:
            return
        if chosen in listed_ids:
            break
        error("Please choose one of the IDs shown in the table above.")
    _show_destination_report(countries.get(chosen))


# تسأل عن عدد الأيام (7 افتراضي، والعميل يختار اللي يناسبه).
def _ask_days() -> int:
    info(f"{DEFAULT_DAYS} days is a good trip: press Enter to accept it, or choose what suits you.")
    return ask_int("Number of days", minimum=MIN_DAYS, maximum=MAX_DAYS, default=DEFAULT_DAYS)


# تسأل عن الأيام وعدد المسافرين (مع عرض خصم شخصين) ومستوى الرحلة.
def _ask_trip_options():
    days = _ask_days()
    info(f"Special offer: if you are {GROUP_SIZE} travelers you get {GROUP_DISCOUNT_PERCENT}% off!")
    travelers = ask_int("Number of travelers", minimum=1, maximum=20, default=1)
    style = ask_choice("Travel style", list(planner.STYLES), default="standard")
    return days, travelers, style


# تسأل عن تاريخ السفر وتكرر إذا غلط، أو None إذا كتب c.
def _ask_date():
    while True:
        raw = ask_text("Travel date (YYYY-MM-DD, or 'c' to cancel)")
        if raw.lower() == "c":
            return None
        try:
            return validators.parse_future_date(raw)
        except ServiceError as exc:
            error(str(exc))


# تسأل عن كود الخصم (أو no) وترجع الكود الصحيح أو نص فاضي.
def _ask_promo_code() -> str:
    while True:
        raw = ask_text("Do you have a discount code? Type it, or type no", "no").strip()
        if raw.lower() in ("no", "n", ""):
            return ""
        try:
            promo = promos.get_active(raw)
        except ServiceError as exc:
            error(str(exc))
            continue
        success(f"Code {promo.code} accepted: {promo.percent}% off ({promo.occasion}).")
        return promo.code


# تحجز: تاريخ وكود خصم ثم الحجز والإيميل والدفع.
def _book(user: User, country, days: int, travelers: int, style: str) -> None:
    date = _ask_date()
    if date is None:
        info("Booking cancelled.")
        return
    promo_code = _ask_promo_code()
    booking = bookings.create(user.id, country.id, date, days, travelers, style, promo_code)
    success(f"Booking #{booking.id} created for {country.city} - status: pending.")
    views.show_breakdown(booking.breakdown, title=f"Your price: {country.city}")
    views.show_mail_result(notifications.notify_booking("created", booking, user))
    if confirm("Continue to payment now?", default=True):
        _pay_booking(user, booking)
    else:
        info("Choose 'Pay for a booking' later to confirm it.")


# تخطيط حسب الميزانية: تعرض الرحلات المناسبة وخطة اللي يختارها.
def plan_trip(user: User) -> None:
    budget = ask_int(f"Your total budget ({CURRENCY})", minimum=1)
    days, travelers, style = _ask_trip_options()
    category = ask_choice("Trip type", ["any", *countries.CATEGORIES], default="any")

    matches, cheapest = planner.find_matches(
        budget, days, travelers, style, "" if category == "any" else category)

    if not matches:
        destination, cost = cheapest
        error("Your budget is not enough for this trip.")
        info(f"Cheapest option: {views.place(destination)} = {views.money(cost['Total'])}")
        warn(f"You need {views.money(cost['Total'] - budget)} more, "
             "or try fewer days / economy style.")
        return

    views.show_plan_options(matches, budget)
    pick = ask_int("Pick a number for the full plan (0 to go back)",
                   minimum=0, maximum=len(matches))
    if pick == 0:
        return
    destination, cost = matches[pick - 1]
    _show_destination_report(destination)
    views.show_itinerary(destination, days)
    views.show_breakdown(cost, budget=budget)
    info("Prices are estimates.")
    if confirm("Book this trip now?"):
        _book(user, destination, days, travelers, style)


# تحجز وجهة بدون تخطيط: تسأل عن الوجهة والأيام والمسافرين ثم تحجز.
def book_trip(user: User) -> None:
    browse()
    country = countries.get(ask_int("Destination ID", minimum=1))
    if country.suspended:
        raise ServiceError(f"{country.city} is suspended until further notice. Please choose another trip.")
    days, travelers, style = _ask_trip_options()
    cost = planner.estimate(country, days, travelers, style)
    views.show_breakdown(cost, title=f"Quote: {views.place(country)}")
    if confirm("Continue with this booking?", default=True):
        _book(user, country, days, travelers, style)


# ترجع حجوزات العميل (ويمكن تصفيتها بشرط).
def _my(user: User, only=None) -> list:
    items = bookings.list_for_user(user.id)
    if only:
        items = [booking for booking in items if only(booking)]
    return items


# تعرض حجوزات العميل.
def my_bookings(user: User) -> None:
    items = _my(user)
    if not items:
        warn("You have no bookings yet.")
        return
    views.show_bookings(items, "My bookings")


# تكرر السؤال لين تكون الإجابة صحيحة حسب دالة التحقق.
def _ask_valid(label: str, is_valid, message: str) -> str:
    while True:
        value = ask_text(label)
        if is_valid(value):
            return value
        error(message)


# تسأل العميل أي حجز يدفع ثم تبدأ الدفع.
def pay(user: User) -> None:
    items = _my(user, lambda booking: booking.status == "pending")
    if not items:
        warn("You have no unpaid bookings.")
        return
    views.show_bookings(items, "Unpaid bookings")
    _pay_booking(user, bookings.get(ask_int("Booking ID to pay", minimum=1), user.id))


# تأخذ طريقة الدفع وبياناتها وتسجل الدفع وترسل الإيصال بالإيميل.
def _pay_booking(user: User, booking) -> None:
    info(f"Amount due: {views.money(booking.total_price)}")
    method = ask_choice("Payment method", bookings.PAYMENT_METHODS, default="card")
    card = {}
    if method == "card":
        info("Demo only: nothing is charged or saved. Use any card number of 8 to 16 digits.")
        card = {
            "card_holder": _ask_valid("Name on card", validators.is_valid_card_holder,
                                      "Use letters only (at least 3)."),
            "card_number": _ask_valid("Card number (8-16 digits)", validators.is_valid_card_number,
                                      "Card number must be 8 to 16 digits."),
            "cvv": _ask_valid("CVV (3 or 4 digits)", validators.is_valid_cvv, "CVV must be 3 or 4 digits."),
        }
    paid = bookings.pay(booking.id, user.id, method, **card)
    success(f"Payment received! Reference: {paid.reference}")
    views.show_mail_result(notifications.notify_booking("paid", paid, user))
    info("Booking confirmed. You can view your receipt from the menu.")


# تلغي حجز العميل بعد تأكيده، وتعرض مبلغ الاسترجاع ومدته.
def cancel(user: User) -> None:
    items = _my(user, lambda booking: booking.status in ("pending", "confirmed"))
    if not items:
        warn("You have no bookings that can be cancelled.")
        return
    views.show_bookings(items, "Cancellable bookings")
    booking_id = ask_int("Booking ID to cancel", minimum=1)
    if not confirm(f"Cancel booking #{booking_id}?"):
        info("Nothing was cancelled.")
        return
    cancelled, refund = bookings.cancel(booking_id, user.id)
    success(f"Booking #{booking_id} cancelled.")
    if refund:
        info(f"Refund amount: {views.money(refund)}. {REFUND_NOTICE}")
    views.show_mail_result(notifications.notify_booking("cancelled", cancelled, user, refund))


# تعرض إيصال حجز مدفوع.
def receipt(user: User) -> None:
    items = _my(user, lambda booking: booking.paid)
    if not items:
        warn("You have no paid bookings yet.")
        return
    views.show_bookings(items, "Paid bookings")
    booking = bookings.receipt(ask_int("Booking ID", minimum=1), user.id)
    views.show_receipt(booking, user.full_name)
