from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style


choices = [
    "View My Profile",
    "Browse Training Courses",
    "Search for a Course",
    "View My Courses",
    "View My Attendance",
    "View My Progress",
    "Log Out",
]

selected = 0



def get_menu():
    lines = [
        ("", "What would you like to do?\n")
    ]

    for index, choice in enumerate(choices):
        if index == selected:
            lines.append(("", "❯ "))

            if choice == "Log Out":
                lines.append((
                    "fg:#ffffff bg:#ff0000",
                    choice
                ))
            else:
                lines.append((
                    "fg:#000000 bg:#ffffff",
                    choice
                ))
        else:
            lines.append(("", "  " + choice))

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


def show_trainee_menu():
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


def trainee_page(user):
    global selected
    selected = 0

    while True:
        print("\n" + "=" * 45)
        print("          MOTQEN ACADEMY")
        print("          TRAINEE PORTAL")
        print("=" * 45)
        print(f"Welcome, {user['full_name']}!")

        choice = show_trainee_menu()

        if choice == "View My Profile":
            print("\n[+] My Profile")
            print(f"Name: {user['full_name']}")
            print(f"Email: {user['email']}")
            print(f"Role: {user['role']}")

        elif choice == "Browse Training Courses":
            print("\nCourse browsing will be added soon.")

        elif choice == "Search for a Course":
            print("\nCourse search will be added soon.")

        elif choice == "View My Courses":
            print("\nYour enrolled courses will appear here.")

        elif choice == "View My Attendance":
            print("\nYour attendance records will appear here.")

        elif choice == "View My Progress":
            print("\nYour training progress will appear here.")

        elif choice == "Log Out" or choice is None:
            print("\nYou have logged out successfully.")
            return

        input("\nPress Enter to continue...")
