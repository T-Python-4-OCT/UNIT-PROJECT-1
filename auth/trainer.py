import json
import os

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style


DATA_FOLDER = "data"
USERS_FILE = os.path.join(DATA_FOLDER, "users.json")
COURSES_FILE = os.path.join(DATA_FOLDER, "courses.json")
ENROLLMENTS_FILE = os.path.join(DATA_FOLDER, "enrollments.json")

choices = [
    "View My Courses",
    "View My Trainees",
    "View Trainee Details",
    "Log Out",
]

selected = 0


def load_data(file_path):
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_menu():
    lines = [
        ("", "TRAINER DASHBOARD\n\n"),
        ("", "Choose an option:\n"),
    ]

    for index, choice in enumerate(choices):
        if index == selected:
            lines.append(("", "❯ "))

            if choice == "Log Out":
                lines.append(("fg:#ffffff bg:#ff0000", choice))
            else:
                lines.append(("fg:#000000 bg:#ffffff", choice))
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


def show_menu():
    control = FormattedTextControl(get_menu)
    window = Window(content=control)
    layout = Layout(HSplit([window]))

    app = Application(
        layout=layout,
        key_bindings=bindings,
        style=Style.from_dict({}),
        full_screen=False,
    )

    return app.run()


def get_trainer_courses(trainer):
    courses = load_data(COURSES_FILE)

    trainer_id = trainer.get("id")
    trainer_name = trainer.get("full_name", "").strip().lower()

    my_courses = []

    for course in courses:
        course_trainer_id = course.get("trainer_id")
        course_trainer_name = course.get("trainer", "").strip().lower()

        if (
            course_trainer_id == trainer_id
            or (
                course_trainer_id is None
                and course_trainer_name == trainer_name
            )
        ):
            my_courses.append(course)

    return my_courses


def get_my_trainees(trainer):
    users = load_data(USERS_FILE)
    enrollments = load_data(ENROLLMENTS_FILE)
    courses = get_trainer_courses(trainer)

    courses_by_id = {
        course["id"]: course
        for course in courses
    }

    trainees = {}

    for enrollment in enrollments:
        course_id = enrollment.get("course_id")
        user_id = enrollment.get("user_id")

        if course_id not in courses_by_id:
            continue

        if enrollment.get("status", "enrolled") != "enrolled":
            continue

        for user in users:
            if (
                user.get("id") == user_id
                and user.get("role") == "trainee"
            ):
                if user_id not in trainees:
                    trainees[user_id] = {
                        "id": user_id,
                        "full_name": user.get("full_name", ""),
                        "email": user.get("email", ""),
                        "courses": [],
                    }

                title = courses_by_id[course_id].get(
                    "title",
                    "Unknown Course",
                )

                if title not in trainees[user_id]["courses"]:
                    trainees[user_id]["courses"].append(title)

                break

    return list(trainees.values())


def print_table(headers, rows):
    if not rows:
        print("\nNo data to display.")
        return

    widths = []

    for index, header in enumerate(headers):
        width = len(str(header))

        for row in rows:
            width = max(width, len(str(row[index])))

        widths.append(width)

    border = "+" + "+".join(
        "-" * (width + 2)
        for width in widths
    ) + "+"

    print(border)

    header_row = "|"

    for index, header in enumerate(headers):
        header_row += " " + str(header).ljust(widths[index]) + " |"

    print(header_row)
    print(border)

    for row in rows:
        data_row = "|"

        for index, value in enumerate(row):
            data_row += " " + str(value).ljust(widths[index]) + " |"

        print(data_row)

    print(border)


def view_my_courses(trainer):
    courses = get_trainer_courses(trainer)

    print("\n" + "=" * 70)
    print("MY COURSES")
    print("=" * 70)

    if not courses:
        print("\nNo courses have been assigned to you.")
        return

    rows = []

    for course in courses:
        rows.append([
            course.get("id", ""),
            course.get("title", ""),
            course.get("duration", ""),
            course.get("price", ""),
        ])

    print_table(
        ["ID", "Course Title", "Duration", "Price (SAR)"],
        rows,
    )

    print(f"\nTotal Courses: {len(courses)}")


def view_my_trainees(trainer):
    trainees = get_my_trainees(trainer)

    print("\n" + "=" * 90)
    print("MY TRAINEES")
    print("=" * 90)

    if not trainees:
        print("\nNo trainees are enrolled in your courses.")
        return

    rows = []

    for trainee in trainees:
        rows.append([
            trainee["id"],
            trainee["full_name"],
            trainee["email"],
            ", ".join(trainee["courses"]),
        ])

    print_table(
        ["ID", "Trainee Name", "Email", "Courses"],
        rows,
    )

    print(f"\nTotal Trainees: {len(trainees)}")


def view_trainee_details(trainer):
    trainees = get_my_trainees(trainer)

    print("\n" + "=" * 50)
    print("TRAINEE DETAILS")
    print("=" * 50)

    if not trainees:
        print("\nNo trainees are enrolled in your courses.")
        return

    trainee_id_text = input("\nEnter Trainee ID: ").strip()

    try:
        trainee_id = int(trainee_id_text)
    except ValueError:
        print("\nPlease enter a valid numeric ID.")
        return

    trainee = next(
        (
            item
            for item in trainees
            if item["id"] == trainee_id
        ),
        None,
    )

    if trainee is None:
        print("\nTrainee not found in your courses.")
        return

    print("\nTrainee Information")
    print("-" * 40)
    print(f"ID: {trainee['id']}")
    print(f"Name: {trainee['full_name']}")
    print(f"Email: {trainee['email']}")

    print("\nEnrolled Courses")
    print("-" * 40)

    for course in trainee["courses"]:
        print(f"- {course}")


def trainer_page(trainer):
    global selected
    selected = 0

    while True:
        print("\n" + "=" * 50)
        print("MOTQEN ACADEMY")
        print("TRAINER DASHBOARD")
        print("=" * 50)
        print(f"Welcome, {trainer['full_name']}!")

        choice = show_menu()

        if choice == "View My Courses":
            view_my_courses(trainer)

        elif choice == "View My Trainees":
            view_my_trainees(trainer)

        elif choice == "View Trainee Details":
            view_trainee_details(trainer)

        elif choice == "Log Out" or choice is None:
            print(f"\nGoodbye, {trainer['full_name']}!")
            print("You have logged out successfully.")
            break

        input("\nPress Enter to continue...")