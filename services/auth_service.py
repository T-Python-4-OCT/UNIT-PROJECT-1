"""
services/auth_service.py
Handles user login and account creation.
"""
import os
from dotenv import load_dotenv
from models.classes import User
from storage import save_data
from utils import (
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_username,
    prompt_name,
    prompt_password,
    prompt_select,
    show_spinner,
    InputCancelled
)

load_dotenv()


def auth_menu(data):
    # Show the welcome menu and return the logged-in user (or None to exit)
    while True:
        print_header(
            "🔐 UniMate — Student Portal",
            "Login or create an account to continue"
        )

        choices = [
            "1. 🔑 Login",
            "2. 📝 Create Account",
            "3. 🚪 Exit"
        ]
        choice = prompt_select("Select an option:", choices)

        if choice is None or "3." in choice:
            return None

        try:
            if "1." in choice:
                user = login_user(data)
            else:
                user = register_user(data)
        except InputCancelled:
            print_info("Cancelled. Back to menu.")
            continue

        if user:
            return user


def login_user(data):
    print_header("🔑 Login", "Enter your username and password")
    users = data.get("users", [])

    if not users:
        print_info("No accounts found. Please create an account first.")
        return None

    env_default_user = os.getenv("DEFAULT_USERNAME", "student")
    username = prompt_username("👤 Username / Student ID:", default_value=env_default_user)
    password = prompt_password("🔒 Password:")

    show_spinner("Checking credentials...")

    target_user = next((u for u in users if u.username.lower() == username.lower()), None)

    if target_user and target_user.check_password(password):
        print_success(f"Welcome back, {target_user.full_name}!")
        return target_user

    print_error("Wrong username or password. Please try again.")
    return None


def register_user(data):
    print_header("📝 Create Account", "Set up your student profile")
    users = data.get("users", [])

    username = prompt_username("👤 Username / Student ID:")
    if any(u.username.lower() == username.lower() for u in users):
        print_error(f"Username '{username}' is already taken.")
        return None

    full_name = prompt_name("🧑 Full Name:")
    default_major = os.getenv("DEFAULT_MAJOR", "Software Engineering")
    major = prompt_name("🎓 Major:", default_value=default_major)
    password = prompt_password("🔒 Password (min 4 characters):", min_length=4)
    confirm_pw = prompt_password("🔒 Confirm Password:")

    if password != confirm_pw:
        print_error("Passwords do not match. Registration cancelled.")
        return None

    new_user = User(username, full_name, major, password)
    show_spinner("Creating your account...")
    data["users"].append(new_user)
    save_data(data)

    print_success(f"Account created! Welcome, {full_name}!")
    return new_user