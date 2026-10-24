from getpass import getpass

from services import auth_service
from storage.seed import seed_if_empty
from ui import reception_menu
from utils.formatters import banner


def login_flow():
    username = input("Username: ")
    password = getpass("Password: ")
    user = auth_service.login(username, password)
    if user is None:
        print("❌ Invalid username or password.\n")
    return user


def main():
    seed_if_empty()
    print("\n🏥", banner(), "\n", sep="\n")
    while True:
        print("1. Login\n2. Exit\n")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            user = login_flow()
            if user:
                print(f"✅ Welcome back, {user.full_name}! (Receptionist)")
                if reception_menu.run(user) == "exit":
                    break
        elif choice == "2":
            break
        else:
            print("❌ Please choose 1 or 2.\n")
    print("Goodbye! 👋")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")