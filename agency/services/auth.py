from agency.config import USERS_FILE
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import users
from agency.storage import json_db
from agency.utils import validators
from agency.utils.security import hash_password, verify_password


# تتحقق من بيانات التسجيل وتنشئ حساب عميل جديد.
def register(username: str, password: str, full_name: str, email: str, phone: str) -> User:
    username = username.strip().lower()
    full_name = full_name.strip()
    email = email.strip().lower()

    if not validators.is_valid_username(username):
        raise ServiceError("Username must be 3-20 characters: letters, numbers or _ only.")
    if not validators.is_valid_password(password):
        raise ServiceError("Password must be at least 6 characters.")
    if not validators.is_valid_full_name(full_name):
        raise ServiceError("Full name must be 2-60 characters.")
    if not validators.is_valid_email(email):
        raise ServiceError("Email address is not valid.")
    phone = validators.normalize_phone(phone)
    if not phone:
        raise ServiceError("Mobile number is not valid: use 8-15 digits, "
                           "for example 0501234567 or +966501234567.")

    records = json_db.load(USERS_FILE)
    if any(user_record["username"] == username for user_record in records):
        raise ServiceError("This username is already taken.")
    if any(user_record["email"] == email for user_record in records):
        raise ServiceError("This email is already registered.")

    user = User(id=users.next_user_id(), username=username,
                password_hash=hash_password(password), full_name=full_name,
                email=email, role="customer", phone=phone)
    records.append(user.to_dict())
    json_db.save(USERS_FILE, records)
    return user


# تتحقق من الاسم وكلمة السر وترجع المستخدم.
def login(username: str, password: str) -> User:
    username = username.strip().lower()
    for user_record in json_db.load(USERS_FILE):
        if user_record["username"] == username and verify_password(password, user_record["password_hash"]):
            return User.from_dict(user_record)
    raise ServiceError("Invalid username or password.")
