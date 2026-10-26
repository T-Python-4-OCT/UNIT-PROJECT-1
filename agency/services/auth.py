"""Registration and login."""
from agency.config import USERS_FILE
from agency.errors import ServiceError
from agency.models.user import User
from agency.services import users
from agency.storage import json_db
from agency.utils import validators
from agency.utils.security import hash_password, verify_password


# تفحص اسم المستخدم (الشكل وأنه غير مأخوذ) وترجعه منظّف.
def check_username(username: str) -> str:
    """The cleaned username, or a ServiceError if it is badly formed or already taken."""
    username = username.strip().lower()
    if not validators.is_valid_username(username):
        raise ServiceError("Username must be 3-20 characters: letters, numbers or _ only.")
    if any(record["username"] == username for record in json_db.load(USERS_FILE)):
        raise ServiceError("This username is already taken.")
    return username


# تفحص أن كلمة السر 6 خانات على الأقل.
def check_password(password: str) -> str:
    """The password itself, or a ServiceError if it is too short."""
    if not validators.is_valid_password(password):
        raise ServiceError("Password must be at least 6 characters.")
    return password


# تفحص الاسم الكامل وترجعه منظّف.
def check_full_name(full_name: str) -> str:
    """The cleaned full name, or a ServiceError."""
    full_name = full_name.strip()
    if not validators.is_valid_full_name(full_name):
        raise ServiceError("Full name must be 2-60 characters.")
    return full_name


# تفحص الإيميل (الشكل وأنه غير مسجّل) وترجعه منظّف.
def check_email(email: str) -> str:
    """The cleaned email, or a ServiceError if it is badly formed or already registered."""
    email = email.strip().lower()
    if not validators.is_valid_email(email):
        raise ServiceError("Email address is not valid.")
    if any(record["email"] == email for record in json_db.load(USERS_FILE)):
        raise ServiceError("This email is already registered.")
    return email


# تفحص رقم الجوال وترجعه منظّف.
def check_phone(phone: str) -> str:
    """The cleaned mobile number, or a ServiceError."""
    cleaned = validators.normalize_phone(phone)
    if not cleaned:
        raise ServiceError("Mobile number is not valid: use 8-15 digits, "
                           "for example 0501234567 or +966501234567.")
    return cleaned


# تتحقق من بيانات التسجيل وتنشئ حساب عميل جديد.
def register(username: str, password: str, full_name: str, email: str, phone: str) -> User:
    """Create a customer account after validating every field."""
    username = check_username(username)
    check_password(password)
    full_name = check_full_name(full_name)
    email = check_email(email)
    phone = check_phone(phone)

    records = json_db.load(USERS_FILE)
    user = User(id=users.next_user_id(), username=username,
                password_hash=hash_password(password), full_name=full_name,
                email=email, role="customer", phone=phone)
    records.append(user.to_dict())
    json_db.save(USERS_FILE, records)
    return user


# تتحقق من الاسم وكلمة السر وترجع المستخدم.
def login(username: str, password: str) -> User:
    """Return the user for a correct username and password, otherwise raise ServiceError."""
    username = username.strip().lower()
    for user_record in json_db.load(USERS_FILE):
        if user_record["username"] == username and verify_password(password, user_record["password_hash"]):
            return User.from_dict(user_record)
    raise ServiceError("Invalid username or password.")
