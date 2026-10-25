from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from courses.course_manager import browse_courses
from courses.course_search import search_course
from auth.users import login_page, create_account_page
from auth.admin import admin_page
from auth.trainee import trainee_page
from auth.trainer import trainer_page
from auth.trainers import view_trainers


base_choices = [
    "Log In",
    "Create Trainee Account",
    "Browse Training Courses",
    "Search for a Course",
    "View Trainers",
    "Verify Certificate",
    "About the Academy",
    "Exit",
]

selected = 0
choices = base_choices.copy()


def get_menu():
    lines = [("class:normal", "Choose an option:\n")]

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
    event.app.invalidate()


@bindings.add("down")
def move_down(event):
    global selected
    selected = (selected + 1) % len(choices)
    event.app.invalidate()


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
    global selected, choices

    logged_in_user = None

    while True:
        if logged_in_user is None:
            choices = base_choices.copy()
        else:
            choices = [
                "Browse Training Courses",
                "Search for a Course",
                "View Trainers",
                "Verify Certificate",
                "About the Academy",
                "Log Out",
                "Exit",
            ]

            if logged_in_user.role == "admin":
                choices.insert(0, "Admin Dashboard")

            elif logged_in_user.role == "trainer":
                choices.insert(0, "Trainer Dashboard")

            elif logged_in_user.role == "trainee":
                choices.insert(0, "My Trainee Dashboard")

        selected = min(selected, len(choices) - 1)

        print("\n" + "=" * 50)

        if logged_in_user is not None:
            print(f"    Welcome, {logged_in_user.full_name}!")

        print("    Learn with Excellence, Grow with Skills")
        print("=" * 50)

        choice = show_menu()

        if choice == "Log In":
            user = login_page()

            if user is not None:
                logged_in_user = user

                if user.role == "admin":
                    result = admin_page(user)

                    if result == "logout":
                        logged_in_user = None

                elif user.role == "trainer":
                    result = trainer_page(user)

                    if result == "logout":
                        logged_in_user = None

                elif user.role == "trainee":
                    result = trainee_page(user)

                    if result == "logout":
                        logged_in_user = None

                else:
                    print("\nUnsupported user role.")
                    logged_in_user = None

        elif choice == "Admin Dashboard":
            if logged_in_user is not None and logged_in_user.role == "admin":
                result = admin_page(logged_in_user)

                if result == "logout":
                    print(f"\nGoodbye, {logged_in_user.full_name}!")
                    logged_in_user = None
                    print("You have logged out successfully.")

        elif choice == "Trainer Dashboard":
            if logged_in_user is not None and logged_in_user.role == "trainer":
                result = trainer_page(logged_in_user)

                if result == "logout":
                    print(f"\nGoodbye, {logged_in_user.full_name}!")
                    logged_in_user = None
                    print("You have logged out successfully.")

        elif choice == "My Trainee Dashboard":
            if logged_in_user is not None and logged_in_user.role == "trainee":
                result = trainee_page(logged_in_user)

                if result == "logout":
                    print(f"\nGoodbye, {logged_in_user.full_name}!")
                    logged_in_user = None
                    print("You have logged out successfully.")

        elif choice == "Create Trainee Account":
            create_account_page()

        elif choice == "Browse Training Courses":
            browse_courses()

        elif choice == "Search for a Course":
            search_course()

        elif choice == "View Trainers":
            view_trainers()

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
                print(f"\nGoodbye, {logged_in_user.full_name}!")
                logged_in_user = None
                print("You have logged out successfully.")

        elif choice == "Exit" or choice is None:
            print("\nThank you for using our system. Goodbye!")
            break

        selected = 0
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()