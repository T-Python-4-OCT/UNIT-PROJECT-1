
from agency.config import USERS_FILE
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import bookings
from agency.storage import json_db


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
