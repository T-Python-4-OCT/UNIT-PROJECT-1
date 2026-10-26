from dataclasses import dataclass, field

from agency.config import USERS_FILE
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import bookings
from agency.storage import json_db


# سطر عميل: حجوزاته وما دفعه.
@dataclass
class CustomerRow:
    user: User
    bookings: int
    active: int
    paid_total: int


# تقرير حذف عميل: الحجوزات الملغية والاسترجاع.
@dataclass
class DeletionReport:
    user: User
    cancelled: list = field(default_factory=list)
    refund_total: int = 0
    kept_history: int = 0


# ترجع كل المستخدمين ككائنات User.
def list_all() -> list:
    return [User.from_dict(record) for record in json_db.load(USERS_FILE)]


# ترجع مستخدم بالرقم أو ترمي ServiceError.
def get(user_id: int) -> User:
    for user in list_all():
        if user.id == user_id:
            return user
    raise ServiceError(f"No customer with ID {user_id}.")


# ترجع قاموس {رقم المستخدم: المستخدم} لعرض اسم الحاجز في قوائم المدير.
def directory() -> dict:
    return {user.id: user for user in list_all()}


# ترجع رقم العميل الجديد (ما يتكرر حتى لو انحذف عميل).
def next_user_id() -> int:
    used = [user.id for user in list_all()] + [booking.user_id for booking in bookings.list_all()]
    return max(used, default=0) + 1


# تبني قائمة العملاء مع عدد حجوزاتهم وإجمالي ما دفعوه.
def customer_overview() -> list:
    all_bookings = bookings.list_all()
    rows = []
    for user in list_all():
        if user.role != "customer":
            continue
        mine = [booking for booking in all_bookings if booking.user_id == user.id]
        rows.append(CustomerRow(
            user=user, bookings=len(mine),
            active=sum(booking.status in bookings.ACTIVE_STATUSES for booking in mine),
            paid_total=sum(booking.total_price for booking in mine if booking.paid)))
    return rows


# ترجع المستخدم وتتأكد أنه عميل (المدير ما ينحذف).
def _customer(user_id: int) -> User:
    user = get(user_id)
    if user.role != "customer":
        raise ServiceError("Only customer accounts can be deleted, not managers.")
    return user


# تجهز تقرير الحذف بدون ما تحذف شي.
def plan_deletion(user_id: int) -> DeletionReport:
    user = _customer(user_id)
    mine = bookings.list_for_user(user_id)
    active = [booking for booking in mine if booking.status in bookings.ACTIVE_STATUSES]
    return DeletionReport(
        user=user,
        cancelled=[(booking, booking.total_price if booking.paid else 0) for booking in active],
        refund_total=sum(booking.total_price for booking in active if booking.paid),
        kept_history=len(mine) - len(active))


# تحذف عميل وتلغي حجوزاته النشطة (مع الاسترجاع) وترجع تقرير الحذف.
def delete_customer(user_id: int) -> DeletionReport:
    plan = plan_deletion(user_id)
    cancelled = bookings.cancel_active_for_user(user_id)
    json_db.save(USERS_FILE, [record for record in json_db.load(USERS_FILE) if record["id"] != user_id])
    return DeletionReport(user=plan.user, cancelled=cancelled,
                          refund_total=sum(refund for _, refund in cancelled),
                          kept_history=plan.kept_history)
