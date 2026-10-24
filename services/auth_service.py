import os
from dotenv import load_dotenv
from models.classes import User
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_required_text,
    prompt_password,
    prompt_select,
    show_spinner
)

# Load environment variables from .env
load_dotenv()

def auth_menu(data):
    """Display login/register screen and return the authenticated User object."""
    while True:
        print_header(
            "StudyMate — Student Portal Authentication",
            "Please login to access your academic dashboard and courses"
        )

        choices = [
            "1. Login to Existing Account",
            "2. Register New Student Account",
            "3. Exit Application"
        ]
        choice = prompt_select("Select an option:", choices)

        if choice is None or "3." in choice:
            return None
        elif "1." in choice:
            user = login_user(data)
            if user:
                return user
        elif "2." in choice:
            user = register_user(data)
            if user:
                return user

def login_user(data):
    print_header("LOGIN: Student Portal", "Enter your credentials")
    users = data.get("users", [])

    if not users:
        print_info("No accounts found. Please register a new account first.")
        return None

    env_default_user = os.getenv("DEFAULT_USERNAME", "student")
    username = prompt_required_text("Enter Username / Student ID:", default_value=env_default_user)
    password = prompt_password("Enter Password:")

    show_spinner("Verifying credentials...")

    target_user = next((u for u in users if u.username.lower() == username.lower()), None)

    if target_user and target_user.check_password(password):
        print_success(f"Welcome back, {target_user.full_name}!")
        return target_user
    else:
        print_error("Invalid username or password. Please try again.")
        return None

def register_user(data):
    print_header("REGISTER: New Student Account", "Create your academic profile")
    users = data.get("users", [])

    username = prompt_required_text("Choose a Username / Student ID:")
    if any(u.username.lower() == username.lower() for u in users):
        print_error(f"Username '{username}' is already taken.")
        return None

    full_name = prompt_required_text("Enter Full Name:")
    default_major = os.getenv("DEFAULT_MAJOR", "Software Engineering")
    major = prompt_required_text("Enter Major:", default_value=default_major)
    password = prompt_password("Create a Password:")
    confirm_pw = prompt_password("Confirm Password:")

    if password != confirm_pw:
        print_error("Passwords do not match! Registration cancelled.")
        return None

    new_user = User(username, full_name, major, password)
    show_spinner("Creating your student profile...")
    data["users"].append(new_user)
    save_data(data)

    print_success(f"Account created successfully! Welcome, {full_name}!")
    return new_user