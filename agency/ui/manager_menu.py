from agency.errors import ServiceError
from agency.models.user import User
from agency.services import bookings, countries, notifications, users
from agency.ui import views
from agency.ui.console import (GoBack, ask_choice, ask_int, console, error, info, pause, success,
                               warn)

MENU = [
    ("2", "List all bookings (with customer details)"),
    ("3", "Update booking status"),
    ("6", "List destinations"),
    ("0", "Logout"),
]


# حلقة قائمة المدير لين يختار الخروج.
def run(user: User) -> None:
    actions = {
        "2": list_bookings,
        "3": update_status,
        "6": list_destinations,
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


# تعرض كل الوجهات للمدير.
def list_destinations() -> None:
    views.show_countries(countries.list_all(), "All destinations")
