from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from auth.users import login_page, create_account_page
from auth.trainee import trainee_page
from auth.trainer import trainer_page


choices = [
    "Log In",
    "Create Trainee Account",
    "Browse Training Courses",
    "Search for a Course",
    "View Trainers",
    "Verify Certificate",
    "About the Academy",
    "Log Out",
    "Exit",
]

selected = 0


def get_menu():
    lines = [
        ("class:normal", "Choose an option:\n")
    ]

    for index, choice in enumerate(choices):
        if index == selected:
            lines.append(("class:pointer", "❯ "))

            if choice == "Exit":
                lines.append(("class:exit", choice))
            else:
                lines.append(("class:highlight", choice))
        else:
            lines.append(("class:normal", "  " + choice))

        lines.append(("", "\n"))

    return lines


bindings = KeyBindings()


@bindings.add("up")
def move_up(event):
    global selected
    selected = (selected - 1) % len(choices)


@bindings.add("down")
def move_down(event):
    global selected
    selected = (selected + 1) % len(choices)


@bindings.add("enter")
def choose(event):
    event.app.exit(result=choices[selected])


style = Style.from_dict({
    "normal": "",
    "pointer": "fg:#ffffff",
    "highlight": "fg:#000000 bg:#ffffff",
    "exit": "fg:#ffffff bg:#ff0000",
})


def show_menu():
    control = FormattedTextControl(get_menu)
    window = Window(content=control)
    layout = Layout(HSplit([window]))

    app = Application(
        layout=layout,
        key_bindings=bindings,
        style=style,
        full_screen=False,
    )

    return app.run()


def main():
    global selected
    logged_in_user = None

    while True:
        print("\n" + "=" * 50)
        print("    Learn with Excellence, Grow with Skills")
        print("=" * 50)

        if logged_in_user:
            print(f"Welcome, {logged_in_user['full_name']}!")
            print(f"Role: {logged_in_user['role']}")

        choice = show_menu()

        if choice == "Log In":
            if logged_in_user is not None:
                print("\nYou are already logged in.")
            else:
                user = login_page()

                if user is not None:
                    logged_in_user = user

                    if user.role == "trainee":
                         trainee_page(user)
                         logged_in_user = None
                    elif user.role == "trainer":
                         trainer_page(user)
                         logged_in_user = None
                    else:
                        print(
                            f"\nWelcome, {user['full_name']}!"
                        )
                        print(f"Role: {user['role']}")

        elif choice == "Create Trainee Account":
            create_account_page()

        elif choice == "Browse Training Courses":
            print("\n[+] Loading Available Courses...")

        elif choice == "Search for a Course":
            print("\n[+] Course Search Engine...")

        elif choice == "View Trainers":
            print("\n[+] Loading Trainers List...")

        elif choice == "Verify Certificate":
            print("\n[+] Certificate Verification Portal...")

        elif choice == "About the Academy":
            print("\n[About Us]")
            print(
                "Learn with Excellence, Grow with Skills. "
                "Our academy is dedicated to providing "
                "top-notch professional training."
            )

        elif choice == "Log Out":
            if logged_in_user is not None:
                print(
                    f"\nGoodbye, {logged_in_user['full_name']}!"
                )
                logged_in_user = None
                print("You have logged out successfully.")
            else:
                print("\nYou are not logged in.")

        elif choice == "Exit" or choice is None:
            print("\nThank you for using our system. Goodbye!")
            break

        selected = 0
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
