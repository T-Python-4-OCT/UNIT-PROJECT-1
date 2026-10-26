from agency.errors import ServiceError
from agency.models.user import User
from agency.config import DEFAULT_PROMO_PERCENT, MAX_PROMO_PERCENT
from agency.services import bookings, countries, notifications, promos, reports, users
from agency.ui import views
from agency.ui.console import (GoBack, ask_choice, ask_int, ask_text, confirm, console,
                               error, info, pause, success, warn)

MENU = [
    ("1", "Dashboard and revenue report"),
    ("2", "List all bookings (with customer details)"),
    ("3", "Update booking status"),
    ("4", "List customers"),
    ("5", "Delete a customer"),
    ("6", "List destinations"),
    ("7", "Add destination"),
    ("8", "Edit destination"),
    ("9", "Delete destination"),
    ("10", "Suspend / resume a trip"),
    ("11", "Discount codes (Eid, year-end...)"),
    ("0", "Logout"),
]


# حلقة قائمة المدير لين يختار الخروج.
def run(user: User) -> None:
    actions = {
        "1": dashboard, "2": list_bookings, "3": update_status,
        "4": list_customers, "5": delete_customer,
        "6": list_destinations, "7": add_destination,
        "8": edit_destination, "9": delete_destination, "10": toggle_suspension,
        "11": discount_codes,
    }
    while True:
        console.print()
        views.show_menu(f"Manager menu - {user.full_name}", MENU, "magenta")

        choice = ask_choice("Choose", [k for k, _ in MENU], allow_back=False)
        if choice == "0":
            info("Logged out.")
            return
        try:
            actions[choice]()
        except GoBack:
            info("Cancelled. Back to the menu.")
            continue
        except ServiceError as exc:
            error(str(exc))
        pause()


# تعرض لوحة المدير: الإيرادات والحجوزات حسب الحالة وأكثر الوجهات.
def dashboard() -> None:
    views.show_report(reports.summary())


# تعرض كل الحجوزات مع بيانات من حجزها.
def list_bookings() -> None:
    items = bookings.list_all()
    if not items:
        warn("There are no bookings yet.")
        return
    views.show_bookings(items, "All bookings", customers=users.directory())


# المدير يغيّر حالة حجز، ويصل العميل إيميل عند الإلغاء أو الإكمال.
def update_status() -> None:
    items = bookings.list_all()
    if not items:
        warn("There are no bookings yet.")
        return
    views.show_bookings(items, "All bookings", customers=users.directory())
    booking_id = ask_int("Booking ID", minimum=1)
    status = ask_choice("New status", bookings.STATUSES)
    booking, refund = bookings.set_status(booking_id, status)
    success(f"Booking #{booking.id} is now {booking.status}.")
    if refund:
        warn(f"Refund due to customer: {views.money(refund)}")
    if status in ("cancelled", "completed"):
        views.show_mail_result(notifications.notify_booking(status, booking, refund=refund))


# تعرض كل العملاء مع حجوزاتهم وما دفعوه.
def list_customers() -> None:
    rows = users.customer_overview()
    if not rows:
        warn("There are no customers yet.")
        return
    views.show_customers(rows)


# تحذف عميل بعد عرض ما سيحصل وتأكيد المدير، وترسل له إيميل.
def delete_customer() -> None:
    rows = users.customer_overview()
    if not rows:
        warn("There are no customers yet.")
        return
    views.show_customers(rows)
    plan = users.plan_deletion(ask_int("Customer ID to delete", minimum=1))
    name = f"{plan.user.full_name} (@{plan.user.username})"
    if plan.cancelled:
        warn(f"{name} has {len(plan.cancelled)} active booking(s). They will be cancelled"
             + (f" and {views.money(plan.refund_total)} refunded." if plan.refund_total else "."))
    if not confirm(f"Delete {name}? This cannot be undone."):
        info("Nothing was deleted.")
        return

    report = users.delete_customer(plan.user.id)
    success(f"Customer {name} deleted.")
    if report.cancelled:
        info(f"{len(report.cancelled)} booking(s) cancelled, refund total {views.money(report.refund_total)}.")
    if report.kept_history:
        info(f"{report.kept_history} past booking(s) stay in the records as history.")
    for booking, refund in report.cancelled:
        views.show_mail_result(notifications.notify_booking("cancelled", booking, report.user, refund))
    views.show_mail_result(notifications.notify_account_deleted(
        report.user, len(report.cancelled), report.refund_total))


# تعرض كل الوجهات للمدير.
def list_destinations() -> None:
    views.show_countries(countries.list_all(), "All destinations")


# تسأل عن بيانات الوجهة (جديدة، أو معدلة مع القيم الحالية كافتراضي).
def _ask_fields(current=None) -> dict:
    # ترجع القيمة الحالية لحقل الوجهة عند التعديل، أو None عند الإضافة.
    def current_value(name):
        return getattr(current, name) if current else None

    data = {
        "country": ask_text("Country", current_value("country")),
        "city": ask_text("Most famous city", current_value("city")),
        "category": ask_choice("Type", countries.CATEGORIES, default=current_value("category")),
    }
    for field, label in [("flight", "Round-trip flight from Riyadh"),
                         ("hotel", "Hotel per night"), ("food", "Food per day"),
                         ("transport", "Transport per day"),
                         ("activities", "Activities per day")]:
        data[field] = ask_int(f"{label} (SAR, per person)", minimum=0, default=current_value(field))
    data["best_season"] = ask_text("Best season", current_value("best_season"))
    data["highlights"] = ask_text("Highlights (comma separated)",
                                  ", ".join(current.highlights) if current else None)
    return data


# تضيف وجهة جديدة.
def add_destination() -> None:
    created = countries.add(_ask_fields())
    success(f"{created.city}, {created.country} added with ID {created.id}.")


# تعدّل وجهة موجودة.
def edit_destination() -> None:
    list_destinations()
    current = countries.get(ask_int("Destination ID to edit", minimum=1))
    info("Press Enter to keep the current value.")
    updated = countries.update(current.id, _ask_fields(current))
    success(f"{updated.city}, {updated.country} updated.")


# توقف رحلة حتى إشعار آخر أو تعيد تشغيلها.
def toggle_suspension() -> None:
    list_destinations()
    current = countries.get(ask_int("Destination ID", minimum=1))
    suspend = not current.suspended
    action = "Suspend" if suspend else "Resume"
    if not confirm(f"{action} {current.city}, {current.country}?"):
        info("No change was made.")
        return
    countries.set_suspended(current.id, suspend)
    if suspend:
        success(f"{current.city} is suspended: customers cannot book it and it is struck through in lists.")
    else:
        success(f"{current.city} is open for booking again.")


# قائمة أكواد الخصم: عرض وإضافة وتشغيل/إيقاف وحذف.
def discount_codes() -> None:
    while True:
        views.show_promos(promos.list_all())
        choice = ask_choice("Codes: [a]dd, [t]oggle on/off, [d]elete, [l]eave", ["a", "t", "d", "l"],
                            default="l", allow_back=False)
        if choice == "l":
            return
        try:
            if choice == "a":
                code = ask_text("New code (letters/numbers, e.g. EID20)")
                occasion = ask_text("Occasion (e.g. Eid Al-Fitr)")
                percent = ask_int(f"Discount percent (max {MAX_PROMO_PERCENT})", minimum=1,
                                  maximum=MAX_PROMO_PERCENT, default=DEFAULT_PROMO_PERCENT)
                promo = promos.add(code, occasion, percent)
                success(f"Code {promo.code} created: {promo.percent}% off for {promo.occasion}.")
            elif choice == "t":
                code = ask_text("Code to switch on/off")
                promo = promos.set_active(code, not promos.get_state(code))
                success(f"Code {promo.code} is now {'active' if promo.active else 'off'}.")
            else:
                code = ask_text("Code to delete")
                if confirm(f"Delete code {promos.normalize(code)}?"):
                    promos.delete(code)
                    success("Code deleted. Bookings that already used it keep their discount.")
        except ServiceError as exc:
            error(str(exc))


# تحذف وجهة بعد التأكيد.
def delete_destination() -> None:
    list_destinations()
    current = countries.get(ask_int("Destination ID to delete", minimum=1))
    if not confirm(f"Delete {current.city}, {current.country}?"):
        info("Nothing was deleted.")
        return
    countries.delete(current.id)
    success(f"{current.city} deleted. Existing bookings keep their details.")
