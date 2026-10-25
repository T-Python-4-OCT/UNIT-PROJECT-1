import json
import os

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from auth.users import load_users, save_users, hash_password


DATA_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)


def load_data(filename):
    path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(filename, data):
    path = os.path.join(DATA_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def create_trainer_account():
    users = load_users()

    name = input("Enter trainer full name: ").strip()
    email = input("Enter trainer email: ").strip().lower()

    if not name or not email:
        print("\nName and email are required.")
        return

    if any(u.get("email", "").lower() == email for u in users):
        print("\nThis email is already registered.")
        return

    import getpass

    password = getpass.getpass("Create trainer password: ")

    if len(password) < 8:
        print("\nPassword must be at least 8 characters.")
        return

    confirm = getpass.getpass("Confirm trainer password: ")

    if password != confirm:
        print("\nPasswords do not match.")
        return

    trainer = {
        "id": max((u.get("id", 0) for u in users), default=0) + 1,
        "full_name": name,
        "email": email,
        "password": hash_password(password),
        "role": "trainer"
    }

    users.append(trainer)
    save_users(users)

    print("\nTrainer account created successfully.")


def view_users(role):
    users = [u for u in load_users() if u.get("role") == role]

    print(f"\n{'=' * 40}\n{role.upper()} ACCOUNTS\n{'=' * 40}")

    if not users:
        print("No accounts found.")
        return

    for user in users:
        print(f"\nID: {user.get('id')}")
        print(f"Name: {user.get('full_name')}")
        print(f"Email: {user.get('email')}")


def view_courses():
    courses = load_data("courses.json")

    print("\nTRAINING COURSES")

    if not courses:
        print("No courses found.")
        return

    for course in courses:
        print(f"\nID: {course.get('id')} | {course.get('title')}")
        print(f"Trainer: {course.get('trainer', 'Not assigned')}")
        print(f"Duration: {course.get('duration', 'Not specified')}")
        print(f"Price: {course.get('price', 'Not specified')} SAR")


def view_lessons():
    lessons = load_data("lessons.json")
    courses = load_data("courses.json")

    print("\nTRAINING LESSONS")

    if not courses:
        print("No courses found.")
        return

    for course in courses:
        print(f"\nCourse: {course.get('title')}")

        course_lessons = sorted(
            [l for l in lessons if l.get("course_id") == course.get("id")],
            key=lambda l: l.get("order", 0)
        )

        if not course_lessons:
            print("No lessons added yet.")
            continue

        for lesson in course_lessons:
            print(f"{lesson.get('order')}. {lesson.get('title')}")
            print(f"   {lesson.get('description', '')}")


def assign_trainer_to_course():
    courses = load_data("courses.json")
    trainers = [u for u in load_users() if u.get("role") == "trainer"]

    if not courses or not trainers:
        print("\nCourses or trainers not found.")
        return

    course_options = [
        f"{c['id']}. {c['title']} (Trainer: {c.get('trainer', 'Not assigned')})"
        for c in courses
    ]

    for option in course_options:
        print(option)

    try:
        course_id = int(input("Enter Course ID: "))
    except ValueError:
        print("Invalid course ID.")
        return

    course = next((c for c in courses if c.get("id") == course_id), None)

    if course is None:
        print("Course not found.")
        return

    for trainer in trainers:
        print(f"{trainer['id']}. {trainer['full_name']} ({trainer['email']})")

    try:
        trainer_id = int(input("Enter Trainer ID: "))
    except ValueError:
        print("Invalid trainer ID.")
        return

    trainer = next((t for t in trainers if t.get("id") == trainer_id), None)

    if trainer is None:
        print("Trainer not found.")
        return

    course["trainer_id"] = trainer["id"]
    course["trainer"] = trainer["full_name"]

    save_data("courses.json", courses)

    print(f"\nTrainer assigned successfully: {trainer['full_name']}")


def view_enrollments():
    enrollments = load_data("enrollments.json")
    users = load_users()
    courses = load_data("courses.json")

    if not enrollments:
        print("\nNo enrollments found.")
        return

    for enrollment in enrollments:
        trainee = next(
            (u for u in users if u.get("id") == enrollment.get("user_id")),
            None
        )

        course = next(
            (c for c in courses if c.get("id") == enrollment.get("course_id")),
            None
        )

        print(f"\nTrainee: {trainee.get('full_name') if trainee else 'Unknown'}")
        print(f"Course: {course.get('title') if course else 'Unknown'}")
        print(f"Date: {enrollment.get('date', 'Not specified')}")
        print(f"Status: {enrollment.get('status', 'Not specified')}")


def view_attendance_reports():
    records = load_data("attendance.json")
    users = load_users()
    courses = load_data("courses.json")

    if not records:
        print("\nNo attendance records found.")
        return

    for record in records:
        trainee_id = record.get("trainee_id", record.get("user_id"))

        trainee = next(
            (u for u in users if u.get("id") == trainee_id),
            None
        )

        course = next(
            (c for c in courses if c.get("id") == record.get("course_id")),
            None
        )

        print(f"\nTrainee: {trainee.get('full_name') if trainee else 'Unknown'}")
        print(f"Course: {course.get('title') if course else 'Unknown'}")
        print(f"Date: {record.get('date', 'Not specified')}")
        print(f"Status: {record.get('status', 'Not specified')}")


choices = [
    "Manage Trainers",
    "Manage Trainees",
    "Manage Courses",
    "Manage Lessons",
    "Assign Trainer to Course",
    "View Enrollments",
    "View Attendance Reports",
    "Create Trainer Account",
    "Back to Main Menu",
    "Log Out"
]

selected = 0


def get_menu():
    lines = [("class:normal", "Choose an option:\n")]

    for index, choice in enumerate(choices):
        if index == selected:
            lines.append(("class:pointer", "❯ "))

            if choice == "Log Out":
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


def show_admin_menu():
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


def admin_page(user):
    global selected
    selected = 0

    while True:
        print(f"\n{'=' * 40}\nADMIN DASHBOARD\n{'=' * 40}")
        print(f"Welcome, {user.full_name}!")

        choice = show_admin_menu()

        if choice is None or choice == "Log Out":
            print("\nYou have logged out successfully.")
            return "logout"

        elif choice == "Manage Trainers":
            view_users("trainer")

        elif choice == "Manage Trainees":
            view_users("trainee")

        elif choice == "Manage Courses":
            view_courses()

        elif choice == "Manage Lessons":
            view_lessons()

        elif choice == "Assign Trainer to Course":
            assign_trainer_to_course()

        elif choice == "View Enrollments":
            view_enrollments()

        elif choice == "View Attendance Reports":
            view_attendance_reports()

        elif choice == "Create Trainer Account":
            create_trainer_account()

        elif choice == "Back to Main Menu":
            return "back"

        input("\nPress Enter to continue...")
