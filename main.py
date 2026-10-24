import sys

from agency import seed
from agency.errors import ServiceError
from agency.services import auth, notifications
from agency.ui import customer_menu, manager_menu, views
from agency.ui.console import (GoBack, ask_choice, ask_password, ask_text, console,
                               error, info, show_banner, success)
from agency.utils import validators


# تسأل عن اسم المستخدم وكلمة السر وتسجل الدخول.
def do_login():
    username = ask_text("Username")
    password = ask_password()
    return auth.login(username, password)


# تسأل عن بيانات التسجيل وتنشئ الحساب وترحب بالعميل.
def do_register():
    username = ask_text("Choose a username")
    full_name = ask_text("Full name")
    email = ask_text("Email (booking confirmations are sent here)")
    phone = ask_text("Mobile number (for example 0501234567)")
    password = ask_password("Choose a password (min 6 characters)")
    if ask_password("Repeat password") != password:
        raise ServiceError("Passwords do not match.")
    user = auth.register(username, password, full_name, email, phone)
    success(f"Account created. Your customer ID is #{user.id}.")
    views.show_mail_result(notifications.notify_welcome(user))
    return user


# تجرب إرسال إيميل للتأكد أن الإعدادات شغالة.
def test_email(address: str) -> None:
    if not validators.is_valid_email(address):
        error("That does not look like an email address.")
        return
    views.show_mail_result(notifications.send_test(address))


# نقطة البداية: الشعار وقائمة الدخول والتسجيل ثم قائمة المدير أو العميل.
def main() -> None:
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
            views.show_welcome(user, [])
            (manager_menu if user.role == "manager" else customer_menu).run(user)
    except (KeyboardInterrupt, EOFError):
        console.print()
    info("Goodbye! Safe travels ✈️")


if __name__ == "__main__":
    main()
