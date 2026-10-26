import os
import re
import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage

from agency.config import APP_NAME, CURRENCY, ENV_FILE, OUTBOX_DIR, REFUND_NOTICE
from agency.errors import ServiceError
from agency.models.booking import Booking
from agency.models.user import User
from agency.services import users
from agency.utils.env_file import read_env_file

TIMEOUT_SECONDS = 10
LOCAL_HOSTNAME = "localhost"
SECURITY_MODES = ("ssl", "starttls", "none")
BOOKING_EVENTS = ("created", "paid", "cancelled", "completed")


# إعدادات السيرفر البريدي (SMTP) المقروءة من .env.
@dataclass
class MailSettings:
    host: str
    port: int
    username: str
    password: str
    sender: str
    security: str


# نتيجة محاولة إرسال إيميل: أُرسل أو انحفظ في outbox أو فشل.
@dataclass
class MailResult:
    status: str
    recipient: str
    detail: str = ""
    outbox_file: str = ""


# تقرأ إعدادات الإيميل من البيئة أو .env، وترجع None إذا ما انضبطت.
def load_settings():
    values = read_env_file(ENV_FILE)
    values.update({key: value for key, value in os.environ.items() if key.startswith("SKYROUTE_")})

    host = values.get("SKYROUTE_SMTP_HOST", "").strip()
    if not host:
        return None
    port_text = values.get("SKYROUTE_SMTP_PORT", "").strip() or "465"
    if not port_text.isdigit():
        raise ServiceError("SKYROUTE_SMTP_PORT must be a number (465 or 587).")
    port = int(port_text)

    security = values.get("SKYROUTE_SMTP_SECURITY", "").strip().lower() or ("ssl" if port == 465 else "starttls")
    if security not in SECURITY_MODES:
        raise ServiceError(f"SKYROUTE_SMTP_SECURITY must be one of: {', '.join(SECURITY_MODES)}.")

    username = values.get("SKYROUTE_SMTP_USER", "").strip()
    sender = values.get("SKYROUTE_MAIL_FROM", "").strip() or username
    if not sender:
        raise ServiceError("Set SKYROUTE_SMTP_USER or SKYROUTE_MAIL_FROM so emails have a sender.")
    return MailSettings(host, port, username, values.get("SKYROUTE_SMTP_PASSWORD", ""), sender, security)


# تحوّل النص إلى سطر واحد (تمنع حقن أسطر إضافية في الإيميل).
def _one_line(text: str) -> str:
    return " ".join(text.split())


# تحفظ الإيميل كملف نصي في data/outbox وترجع مساره.
def _save_to_outbox(to_address: str, subject: str, body: str) -> str:
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    name = f"{now:%Y%m%d-%H%M%S-%f}-{re.sub(r'[^A-Za-z0-9]+', '_', to_address)}.txt"
    text = f"To: {to_address}\nSubject: {subject}\nDate: {now:%Y-%m-%d %H:%M:%S}\n\n{body}\n"
    (OUTBOX_DIR / name).write_text(text, encoding="utf-8")
    return name


# ترسل الرسالة فعلياً عبر SMTP.
def _deliver(settings: MailSettings, message: EmailMessage) -> None:


    if settings.security == "ssl":
        client = smtplib.SMTP_SSL(settings.host, settings.port, local_hostname=LOCAL_HOSTNAME,
                                  timeout=TIMEOUT_SECONDS, context=ssl.create_default_context())
    else:
        client = smtplib.SMTP(settings.host, settings.port, local_hostname=LOCAL_HOSTNAME,
                              timeout=TIMEOUT_SECONDS)
    with client:
        if settings.security == "starttls":
            client.starttls(context=ssl.create_default_context())
        if settings.username:
            client.login(settings.username, settings.password)
        client.send_message(message)


# ترسل إيميل، وإذا فشل أو ما انضبط تحفظ نسخة في outbox بدون ما توقف البرنامج.
def send_email(to_address: str, subject: str, body: str) -> MailResult:
    subject = _one_line(subject)

    # تبني نتيجة 'ما انرسل' وتحفظ نسخة من الإيميل في outbox.
    def not_sent(status: str, detail: str = "") -> MailResult:
        return MailResult(status, to_address, detail, _save_to_outbox(to_address, subject, body))

    try:
        settings = load_settings()
    except ServiceError as exc:
        return not_sent("failed", str(exc))
    if settings is None:
        return not_sent("saved")

    try:
        message = EmailMessage()
        message["From"] = settings.sender
        message["To"] = to_address
        message["Subject"] = subject
        message.set_content(body)
    except ValueError as exc:
        return not_sent("failed", f"The email could not be built: {exc}")

    try:
        _deliver(settings, message)
    except smtplib.SMTPAuthenticationError:
        return not_sent("failed", "The mail server rejected the username or password "
                                  "(Gmail needs an App Password, not the normal password).")
    except (smtplib.SMTPException, OSError) as exc:
        return not_sent("failed", f"Could not reach the mail server: {exc}")
    except UnicodeError as exc:
        return not_sent("failed", f"The email contains a character the mail server cannot take: {exc}")
    return MailResult("sent", to_address)


# تنسق المبلغ مع العملة، مثل 1,200 SAR.
def _money(value) -> str:
    return f"{value:,.0f} {CURRENCY}"


# تبني أسطر تفاصيل الرحلة اللي تنكتب في الإيميل.
def _trip_lines(booking: Booking) -> str:
    lines = [
        f"  Booking     : #{booking.id}",
        f"  Trip        : {booking.city}, {booking.country}",
        f"  Travel date : {booking.travel_date}",
        f"  Duration    : {booking.days} days, {booking.travelers} traveler(s), {booking.style} style",
        f"  Total       : {_money(booking.total_price)}",
    ]
    if booking.promo_code:
        lines.insert(-1, f"  Discount    : code {booking.promo_code}")
    return "\n".join(lines)


# توقيع الإيميل في آخر الرسالة.
def _signature() -> str:
    return f"\nSafe travels,\nThe {APP_NAME} team"


# تبني موضوع ونص إيميل الترحيب بعد التسجيل.
def build_welcome(user: User) -> tuple:
    body = (f"Hello {user.full_name},\n\nWelcome to {APP_NAME}! Your account is ready.\n\n"
            f"  Customer ID : #{user.id}\n  Username    : {user.username}\n  Email       : {user.email}\n\n"
            "Plan a trip by budget, check the live weather, then book and pay in a few steps. "
            "Booking and payment confirmations will be sent to this address."
            + _signature())
    return f"Welcome to {APP_NAME}, {user.full_name.split()[0]}!", body


# تبني موضوع ونص إيميل الحجز حسب الحدث: إنشاء أو دفع أو إلغاء أو إكمال.
def build_booking_message(event: str, booking: Booking, user: User, refund: int = 0) -> tuple:
    if event not in BOOKING_EVENTS:
        raise ValueError(f"Unknown booking event: {event}")
    greeting = f"Hello {user.full_name},\n\n"

    if event == "created":
        subject = f"{APP_NAME}: booking #{booking.id} received ({booking.city})"
        text = ("We received your booking request.\n\n" + _trip_lines(booking)
                + "\n  Status      : pending payment\n\n"
                "Open the program and choose 'Pay for a booking' to confirm your trip.")
    elif event == "paid":
        subject = f"{APP_NAME}: payment confirmed - {booking.reference}"
        costs = "\n".join(f"  {item:<22}{_money(value):>14}" for item, value in booking.breakdown.items()
                          if item != "Total")
        text = (f"Thank you! Your payment was received and your trip is confirmed.\n\n"
                f"  Reference   : {booking.reference}\n  Payment     : {booking.payment_method.replace('_', ' ')}\n"
                + _trip_lines(booking) + f"\n\nCost breakdown\n{costs}\n\nKeep this email as your receipt.")
    elif event == "cancelled":
        subject = f"{APP_NAME}: booking #{booking.id} cancelled"
        money_line = (f"Refund amount: {_money(refund)}\n{REFUND_NOTICE}" if refund
                      else "No payment was taken for this booking, so there is nothing to refund.")
        text = f"Your booking was cancelled.\n\n{_trip_lines(booking)}\n\n{money_line}"
    else:
        subject = f"{APP_NAME}: your {booking.city} trip is completed"
        text = (f"Your trip is now marked as completed. We hope you had a wonderful time!\n\n"
                + _trip_lines(booking))
    return subject, greeting + text + "\n" + _signature()


# تبني إيميل إشعار حذف الحساب مع الحجوزات الملغية والاسترجاع.
def build_account_deleted(user: User, cancelled_count: int, refund_total: int) -> tuple:
    lines = [f"Hello {user.full_name},\n", f"Your {APP_NAME} account (@{user.username}) has been deleted "
             "by the agency manager."]
    if cancelled_count:
        lines.append(f"{cancelled_count} active booking(s) were cancelled.")
    if refund_total:
        lines.append(f"Refund amount: {_money(refund_total)}. {REFUND_NOTICE}")
    lines.append("If you think this is a mistake, please contact the agency.")
    return f"{APP_NAME}: your account was deleted", "\n".join(lines) + "\n" + _signature()


# ترسل إيميل تجريبي للتأكد من الإعدادات.
def send_test(address: str) -> MailResult:
    return send_email(address, f"{APP_NAME}: test email",
                      f"Hello!\n\nIf you can read this on your phone, the {APP_NAME} email settings work."
                      + _signature())


# ترسل إيميل الترحيب للعميل الجديد وترجع نتيجة الإرسال.
def notify_welcome(user: User) -> MailResult:
    subject, body = build_welcome(user)
    return send_email(user.email, subject, body)


# ترسل إيميل الحجز (إنشاء أو دفع أو إلغاء أو إكمال) وترجع نتيجة الإرسال.
def notify_booking(event: str, booking: Booking, user=None, refund: int = 0) -> MailResult:
    if user is None:
        try:
            user = users.get(booking.user_id)
        except ServiceError:
            return MailResult("failed", "", "The customer account was not found.")
    subject, body = build_booking_message(event, booking, user, refund)
    return send_email(user.email, subject, body)


# ترسل إيميل حذف الحساب وترجع نتيجة الإرسال.
def notify_account_deleted(user: User, cancelled_count: int = 0, refund_total: int = 0) -> MailResult:
    subject, body = build_account_deleted(user, cancelled_count, refund_total)
    return send_email(user.email, subject, body)
