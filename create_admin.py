import questionary
from auth.users import load_users, save_users, hash_password


def create_admin():
    users = load_users()

    if any(user.get("role") == "admin" for user in users):
        print("\nAn admin account already exists.")
        return

    print("\n" + "=" * 40)
    print("       CREATE ADMIN ACCOUNT")
    print("=" * 40)

    full_name = questionary.text(
        "Enter admin full name:"
    ).ask()

    if not full_name or not full_name.strip():
        print("\nName is required.")
        return

    email = questionary.text(
        "Enter admin email:"
    ).ask()

    if not email or not email.strip():
        print("\nEmail is required.")
        return

    email = email.strip().lower()

    if any(user.get("email", "").lower() == email for user in users):
        print("\nThis email is already registered.")
        return

    password = questionary.password(
        "Create admin password:"
    ).ask()

    if password is None or len(password) < 8:
        print("\nPassword must be at least 8 characters.")
        return

    confirm_password = questionary.password(
        "Confirm admin password:"
    ).ask()

    if confirm_password is None:
        return

    if password != confirm_password:
        print("\nPasswords do not match.")
        return

    new_admin = {
        "id": max(
            (user.get("id", 0) for user in users),
            default=0
        ) + 1,
        "full_name": full_name.strip(),
        "email": email,
        "password": hash_password(password),
        "role": "admin"
    }

    users.append(new_admin)
    save_users(users)

    print("\nAdmin account created successfully.")
    print("You can now log in using your admin account.")


if __name__ == "__main__":
    create_admin()
