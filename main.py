"""SkyRoute entry point: welcome menu, login and register."""
import sys

from agency import seed
from agency.errors import ServiceError
from agency.services import auth, notifications, reports
from agency.ui import customer_menu, manager_menu, views
from agency.ui.console import (GoBack, ask_choice, ask_password, ask_text, console,
                               error, info, show_banner, success)
from agency.utils import sound, validators


# تسأل عن اسم المستخدم وكلمة السر وتسجل الدخول.
def do_login():
    """Ask for credentials and log in."""
    username = ask_text("Username")
    password = ask_password()
    return auth.login(username, password)


# تسأل السؤال وتفحص الجواب فوريًا؛ إذا خطأ تطبع الخطأ وتعيد نفس السؤال.
def ask_checked(label: str, check):
    """Ask until the answer passes `check`; a wrong answer shows the error and asks the same question again."""
    while True:
        value = ask_text(label)
        try:
            return check(value)
        except ServiceError as exc:
            error(str(exc))


# تسأل عن كلمة السر وتكرارها وتعيد السؤال لين يصيران صح.
def ask_new_password() -> str:
    """Ask for a password (at least 6 characters) and its repetition, until both are right."""
    while True:
        password = ask_password("Choose a password (min 6 characters)")
        try:
            auth.check_password(password)
        except ServiceError as exc:
            error(str(exc))
            continue
        if ask_password("Repeat password") == password:
            return password
        error("Passwords do not match. Try again.")


# تسأل عن بيانات التسجيل وتنشئ الحساب وترحب بالعميل.
def do_register():
    """Ask for the new account details, checking every answer on the spot, and register."""
    username = ask_checked("Choose a username", auth.check_username)
    full_name = ask_checked("Full name", auth.check_full_name)
    email = ask_checked("Email (booking confirmations are sent here)", auth.check_email)
    phone = ask_checked("Mobile number (for example 0501234567)", auth.check_phone)
    password = ask_new_password()
    user = auth.register(username, password, full_name, email, phone)
    success(f"Account created. Your customer ID is #{user.id}.")
    views.show_mail_result(notifications.notify_welcome(user))
    return user


# تجرب إرسال إيميل للتأكد أن الإعدادات شغالة.
def test_email(address: str) -> None:
    """`python main.py --test-email you@gmail.com`: send one test email and show the result."""
    if not validators.is_valid_email(address):
        error("That does not look like an email address.")
        return
    views.show_mail_result(notifications.send_test(address))


# نقطة البداية: الشعار وقائمة الدخول والتسجيل ثم قائمة المدير أو العميل.
def main() -> None:
    """Program entry: seed data, banner, welcome menu, then the role's menu."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    seed.run()
    if len(sys.argv) == 3 and sys.argv[1] == "--test-email":
        test_email(sys.argv[2])
        return
    show_banner()
    try:
        while True:
            console.print("\n[bold]1[/bold] Login   [bold]2[/bold] Register   [bold red]0[/bold red] Exit")
            console.print("[dim]Tip: type b at any question to go back[/dim]")
            choice = ask_choice("Choose", ["1", "2", "0"], allow_back=False)
            if choice == "0":
                break
            try:
                user = do_login() if choice == "1" else do_register()
            except GoBack:
                info("Back to the main menu.")
                continue
            except ServiceError as exc:
                error(str(exc))
                continue
            if choice == "1":
                sound.welcome()
            views.show_welcome(user, reports.welcome_notes(user))
            (manager_menu if user.role == "manager" else customer_menu).run(user)
    except (KeyboardInterrupt, EOFError):
        console.print()
    info("Goodbye! Safe travels ✈️")


if __name__ == "__main__":
    main()
