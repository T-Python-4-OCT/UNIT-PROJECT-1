import json
import os
import hashlib
import questionary
from models.trainee import Trainee
from models.trainer import Trainer


DATA_FOLDER = "data"
USERS_FILE = os.path.join(DATA_FOLDER, "users.json")



def setup_users_file():
    os.makedirs(DATA_FOLDER, exist_ok=True)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def load_users():
    setup_users_file()

    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_account_page():
    print("\n" + "=" * 40)
    print("       CREATE TRAINEE ACCOUNT")
    print("=" * 40)

    full_name = questionary.text(
        "Enter your full name:"
    ).ask()

    if not full_name or not full_name.strip():
        print("\nName is required.")
        return

    email = questionary.text(
        "Enter your email:"
    ).ask()

    if not email or not email.strip():
        print("\nEmail is required.")
        return

    email = email.strip().lower()

    users = load_users()

    # Check whether the email is already registered
    for user in users:
        if user["email"].lower() == email:
            print("\nThis email is already registered.")
            return

    password = questionary.password(
        "Create your password:"
    ).ask()

    if password is None or len(password) < 8:
        print("\nPassword must be at least 8 characters.")
        return

    confirm_password = questionary.password(
        "Confirm your password:"
    ).ask()

    if confirm_password is None:
        return

    if password != confirm_password:
        print("\nPasswords do not match.")
        return

    # Create the new user
    new_user = {
        "id": max(
            (user.get("id", 0) for user in users),
            default=0
        ) + 1,
        "full_name": full_name.strip(),
        "email": email,
        "password": hash_password(password),
        "role": "trainee"
    }

    users.append(new_user)
    save_users(users)

    print("\nAccount created successfully!")
    print("You can now log in using your email and password.")


# Login
def login_page():
    print("\n" + "=" * 40)
    print("          MOTQEN ACADEMY")
    print("              LOG IN")
    print("=" * 40)

    email = questionary.text(
        "Enter your email:"
    ).ask()

    if not email:
        return None

    password = questionary.password(
        "Enter your password:"
    ).ask()

    if password is None:
        return None

    users = load_users()
    password_hash = hash_password(password)

    for user in users:
        if (
            user["email"].lower() == email.strip().lower()
            and user["password"] == password_hash
        ):
            if user["role"] == "trainee":
                logged_in_user = Trainee(
                    user["id"],
                    user["full_name"],
                    user["email"]
                )
            elif user["role"] == "trainer":
                logged_in_user = Trainer(
                    user["id"],
                    user["full_name"],
                    user["email"]
                )
            else:
                print("\nThis user role is not supported.")
                return None

            print(f"\nWelcome back, {logged_in_user.full_name}!")
            print(f"Your role: {logged_in_user.role}")

            return logged_in_user

    print("\nInvalid email or password.")
    return None


# Ensure the users file exists
setup_users_file()