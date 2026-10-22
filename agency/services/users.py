
from agency.config import USERS_FILE
from agency.errors import ServiceError
from agency.models.user import User
from agency.storage import json_db


def list_all() -> list:
    return [User.from_dict(record) for record in json_db.load(USERS_FILE)]


def get(user_id: int) -> User:
    for user in list_all():
        if user.id == user_id:
            return user
    raise ServiceError(f"No customer with ID {user_id}.")


def directory() -> dict:
    return {user.id: user for user in list_all()}


def next_user_id() -> int:
    used = [user.id for user in list_all()]
    return max(used, default=0) + 1
