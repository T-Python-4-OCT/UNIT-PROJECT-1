"""Customer menu: browse, search, plan, book, pay, cancel, receipts and recommendations."""
from rich.markup import escape

from agency.config import (CURRENCY, DEFAULT_DAYS, GROUP_DISCOUNT_PERCENT, GROUP_SIZE,
                           MAX_DAYS, MIN_DAYS, REFUND_NOTICE, YEAR_END_PROMO_PERCENT)
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import (bookings, countries, notifications, planner,
                             promos, recommendations, weather)
from agency.ui import views
from agency.ui.console import (GoBack, ask_choice, ask_int, ask_text,
                               confirm, console, error, heading, info, pause,
                               success, warn)
from agency.utils import sound, validators

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
    ("10", "Recommendations for me"),
    ("0", "Logout"),
]


# حلقة قائمة العميل لين يختار الخروج.
def run(user: User) -> None:
    """Customer main loop: show the menu, run the chosen action, handle errors."""
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
        "10": lambda: recommend(user),
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


# ---------- browsing ----------
# تعرض عرض الشخصين (خصم 10%) وملاحظة كود نهاية السنة بالأخضر.
def _show_offers() -> None:
    info(f"Special offer: if you are {GROUP_SIZE} travelers you get {GROUP_DISCOUNT_PERCENT}% off!")
    console.print(f"[cyan]Note: in December there is an extra year-end discount code "
                  f"({YEAR_END_PROMO_PERCENT}% off):[/cyan] [bold green]{promos.YEAR_END_CODE}[/bold green]")


# تعرض كل الوجهات في جدول.
def browse() -> None:
    """Show every destination."""
    views.show_countries(countries.list_all(), "All destinations")
    _show_offers()


# تعرض الوجهات ثم تسأل عن رقم وجهة وتعرض تفاصيلها مع الطقس.
def details() -> None:
    """Show one destination's details and its live weather."""
    views.show_countries(countries.list_all(), "All destinations")
    _show_destination_report(countries.get(ask_int("Destination ID", minimum=1)))


# تعرض تفاصيل الوجهة ثم الطقس الحي.
def _show_destination_report(destination, days: int = DEFAULT_DAYS,
                             travelers: int = None, style: str = "standard") -> None:
    """The city information (highlights, costs, season) plus its live weather.
    Shared by the details, search and budget-plan screens so they show the same facts."""
    views.show_country_detail(destination, days, travelers, style)
    if travelers is None:
        _show_offers()
    _show_live_weather(destination)


# تجيب الطقس وتعرضه، وإذا فشل (ما فيه إنترنت) تعرض تنبيه أصفر وتكمل.
def _show_live_weather(destination) -> None:
    """Fetch and show the weather. A failure here is only a warning, not an error."""
    try:
        with console.status("[cyan]Fetching live weather...[/cyan]"):
            report = weather.get_forecast(destination)
    except ServiceError as exc:
        warn(str(exc))
        return
    views.show_weather(report)


# تبحث في الوجهات بالدولة أو المدينة أو النوع (مع تصحيح الإملاء).
def search() -> None:
    """Search destinations by country, city or type (city / beach / culture / adventure)."""
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
    _show_offers()
    _offer_details(results)


# تسأل عن رقم من نتائج البحث وتعرض تفاصيله مع الطقس.
def _offer_details(results) -> None:
    """Let the customer open one of the listed destinations: city details + live weather."""
    listed_ids = {destination.id for destination in results}
    while True:
        chosen = ask_int("Enter an ID to see its details and live weather (0 to skip)", minimum=0)
        if chosen == 0:
            return
        if chosen in listed_ids:
            break
        error("Please choose one of the IDs shown in the table above.")
    _show_destination_report(countries.get(chosen))


# ---------- planning and booking ----------
# تسأل عن عدد الأيام (7 افتراضي، والعميل يختار اللي يناسبه).
def _ask_days() -> int:
    """Ask for the trip length. 7 days is suggested, but any length from 2 to 30 is allowed."""
    info(f"{DEFAULT_DAYS} days is a good trip: press Enter to accept it, or choose what suits you.")
    return ask_int("Number of days", minimum=MIN_DAYS, maximum=MAX_DAYS, default=DEFAULT_DAYS)


# تسأل عن الأيام وعدد المسافرين (مع عرض خصم شخصين) ومستوى الرحلة.
def _ask_trip_options():
    """Ask for days, travelers and travel style."""
    days = _ask_days()
    info(f"Special offer: if you are {GROUP_SIZE} travelers you get {GROUP_DISCOUNT_PERCENT}% off!")
    travelers = ask_int("Number of travelers", minimum=1, maximum=20, default=1)
    style = ask_choice("Travel style", list(planner.STYLES), default="standard")
    return days, travelers, style


# تسأل عن تاريخ السفر وتكرر إذا غلط، أو None إذا كتب c.
def _ask_date():
    """Ask until the date is valid. Returns None if the user cancels."""
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
    """Ask for a discount code until it is accepted. Answering 'no' (or Enter) skips it.
    Returns the code, or "" when the customer has none."""
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
    """Ask for a travel date and a discount code, create the booking, then move on to payment."""
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
    """Suggest trips that fit the user's budget, then optionally book one."""
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
    _show_destination_report(destination, days, travelers, style)
    views.show_itinerary(destination, days)
    views.show_breakdown(cost, budget=budget)
    info("Prices are estimates.")
    if confirm("Book this trip now?"):
        _book(user, destination, days, travelers, style)


# تحجز وجهة بدون تخطيط: تسأل عن الوجهة والأيام والمسافرين ثم تحجز.
def book_trip(user: User) -> None:
    """Book a chosen destination directly."""
    browse()
    country = countries.get(ask_int("Destination ID", minimum=1))
    if country.suspended:  # fail early, before the customer fills in days, travelers and date
        raise ServiceError(f"{country.city} is suspended until further notice. Please choose another trip.")
    days, travelers, style = _ask_trip_options()
    cost = planner.estimate(country, days, travelers, style)
    views.show_breakdown(cost, title=f"Quote: {views.place(country)}")
    if confirm("Continue with this booking?", default=True):
        _book(user, country, days, travelers, style)


# ---------- my bookings ----------
# ترجع حجوزات العميل (ويمكن تصفيتها بشرط).
def _my(user: User, only=None) -> list:
    """This customer's bookings, optionally filtered by a condition."""
    items = bookings.list_for_user(user.id)
    if only:
        items = [booking for booking in items if only(booking)]
    return items


# تعرض حجوزات العميل.
def my_bookings(user: User) -> None:
    """List the customer's bookings."""
    items = _my(user)
    if not items:
        warn("You have no bookings yet.")
        return
    views.show_bookings(items, "My bookings")


# تكرر السؤال لين تكون الإجابة صحيحة حسب دالة التحقق.
def _ask_valid(label: str, is_valid, message: str) -> str:
    """Ask until the answer passes `is_valid`, so a typo does not restart the payment."""
    while True:
        value = ask_text(label)
        if is_valid(value):
            return value
        error(message)


# تسأل العميل أي حجز يدفع ثم تبدأ الدفع.
def pay(user: User) -> None:
    """Pay for one of the customer's pending bookings."""
    items = _my(user, lambda booking: booking.status == "pending")
    if not items:
        warn("You have no unpaid bookings.")
        return
    views.show_bookings(items, "Unpaid bookings")
    _pay_booking(user, bookings.get(ask_int("Booking ID to pay", minimum=1), user.id))


# تأخذ طريقة الدفع وبياناتها وتسجل الدفع وترسل الإيصال بالإيميل.
def _pay_booking(user: User, booking) -> None:
    """Ask how the customer pays, take the payment and send the confirmation."""
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
    """Cancel a booking (shows the refund if it was paid)."""
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
    """Show the receipt of a paid booking."""
    items = _my(user, lambda booking: booking.paid)
    if not items:
        warn("You have no paid bookings yet.")
        return
    views.show_bookings(items, "Paid bookings")
    booking = bookings.receipt(ask_int("Booking ID", minimum=1), user.id)
    try:
        destination = countries.get(booking.country_id)   # may be gone if the manager deleted it
    except ServiceError:
        destination = None
    day_weather, weather_note = None, ""
    if destination:
        try:
            with console.status(f"[cyan]Checking the weather for {escape(booking.travel_date)}...[/cyan]"):
                day_weather = weather.get_day_forecast(destination, booking.travel_date)
            if day_weather is None:
                weather_note = "no forecast yet (it appears 16 days before the trip)"
        except ServiceError:      # weather is a bonus: the receipt must still show
            weather_note = "not available right now"
    views.show_receipt(booking, user.full_name, destination, day_weather, weather_note)
    sound.receipt_sound()


# تسأل عن نوع الرحلة والأيام وتعرض توصيات مع الطقس والخطة.
def recommend(user: User) -> None:
    """Ask for a trip type and length, then show matching trips with city, type, weather and a day-by-day plan."""
    category = ask_choice("Which trip type do you want", ["any", *countries.CATEGORIES], default="any")
    days = _ask_days()
    picks = recommendations.recommend(user.id, category="" if category == "any" else category)
    if not picks:
        warn(f"No {category} trips to recommend right now.")
        return
    heading("Recommended for you")
    for destination, reason in picks:
        try:
            with console.status(f"[cyan]Fetching weather for {escape(destination.city)}...[/cyan]"):
                report = weather.get_forecast(destination)
        except ServiceError:  # weather is a bonus: still show the trip without it
            report = None
        views.show_recommendation(destination, reason, report, days)
