import json
import os
import getpass

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


# ==================== JSON ====================

def load_data(filename):
    path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(filename, data):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    path = os.path.join(DATA_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# ==================== ARROW MENU ====================

STYLE = Style.from_dict({
    "normal": "",
    "pointer": "fg:#ffffff",
    "highlight": "fg:#000000 bg:#ffffff",
    "exit": "fg:#ffffff bg:#ff0000",
})


def arrow_menu(title, choices):
    selected = 0

    def get_menu():
        lines = [
            ("", f"\n{'=' * 40}\n"),
            ("", f"{title.center(40)}\n"),
            ("", f"{'=' * 40}\n\n"),
            ("", "Choose an option:\n\n"),
        ]

        for index, choice in enumerate(choices):
            if index == selected:
                lines.append(("class:pointer", "❯ "))

                if choice in ("Back", "Back to Main Menu", "Log Out"):
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
        nonlocal selected
        selected = (selected - 1) % len(choices)
        event.app.invalidate()

    @bindings.add("down")
    def move_down(event):
        nonlocal selected
        selected = (selected + 1) % len(choices)
        event.app.invalidate()

    @bindings.add("enter")
    def choose(event):
        event.app.exit(result=choices[selected])

    @bindings.add("c-c")
    def cancel(event):
        event.app.exit(result=None)

    app = Application(
        layout=Layout(
            HSplit([
                Window(content=FormattedTextControl(get_menu))
            ])
        ),
        key_bindings=bindings,
        style=STYLE,
        full_screen=False,
    )

    return app.run()


# ==================== HELPERS ====================

def next_id(items):
    return max((item.get("id", 0) for item in items), default=0) + 1


def select_record(title, items, label):
    if not items:
        print("\nNo records found.")
        return None

    choices = [
        f"{item['id']} - {label(item)}"
        for item in items
    ]
    choices.append("Back")

    choice = arrow_menu(title, choices)

    if not choice or choice == "Back":
        return None

    record_id = int(choice.split(" - ", 1)[0])

    return next(
        (item for item in items if item.get("id") == record_id),
        None
    )


def get_value(label, current=""):
    value = input(f"{label} [{current}]: ").strip()
    return value if value else current


def confirm(message):
    return input(f"{message} (y/n): ").strip().lower() == "y"


# ==================== TRAINERS ====================

def create_trainer_account():
    users = load_users()

    name = input("Trainer full name: ").strip()
    email = input("Trainer email: ").strip().lower()

    if not name or not email:
        print("Name and email are required.")
        return

    if any(u.get("email", "").lower() == email for u in users):
        print("Email already registered.")
        return

    password = getpass.getpass("Password: ")

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        return

    if password != getpass.getpass("Confirm password: "):
        print("Passwords do not match.")
        return

    users.append({
        "id": next_id(users),
        "full_name": name,
        "email": email,
        "password": hash_password(password),
        "role": "trainer",
    })

    save_users(users)
    print("Trainer created successfully.")


def view_users(role):
    users = [u for u in load_users() if u.get("role") == role]

    print(f"\n{role.upper()} ACCOUNTS")

    if not users:
        print("No accounts found.")
        return

    for user in users:
        print(
            f"\nID: {user.get('id')}\n"
            f"Name: {user.get('full_name')}\n"
            f"Email: {user.get('email')}"
        )


def edit_user(role):
    users = load_users()
    records = [u for u in users if u.get("role") == role]

    user = select_record(
        f"EDIT {role.upper()}",
        records,
        lambda u: u.get("full_name", "")
    )

    if not user:
        return

    name = get_value("Name", user.get("full_name", ""))
    email = get_value("Email", user.get("email", "")).lower()

    if any(
        u.get("id") != user.get("id")
        and u.get("email", "").lower() == email
        for u in users
    ):
        print("Email already registered.")
        return

    user["full_name"] = name
    user["email"] = email
    save_users(users)

    if role == "trainer":
        courses = load_data("courses.json")

        for course in courses:
            if course.get("trainer_id") == user.get("id"):
                course["trainer"] = name

        save_data("courses.json", courses)

    print("Account updated successfully.")


def delete_user(role):
    users = load_users()
    records = [u for u in users if u.get("role") == role]

    user = select_record(
        f"DELETE {role.upper()}",
        records,
        lambda u: u.get("full_name", "")
    )

    if not user:
        return

    user_id = user["id"]

    if role == "trainer":
        courses = load_data("courses.json")

        if any(c.get("trainer_id") == user_id for c in courses):
            print("Reassign this trainer's courses before deleting.")
            return

    if role == "trainee":
        for filename in (
            "enrollments.json",
            "attendance.json",
            "grades.json",
            "progress.json",
            "lesson_progress.json",
        ):
            records = load_data(filename)

            if any(
                r.get("user_id") == user_id
                or r.get("trainee_id") == user_id
                for r in records
            ):
                print(f"Related records exist in {filename}.")
                print("Account was not deleted.")
                return

    if confirm(f"Delete {user.get('full_name')}?"):
        save_users([u for u in users if u.get("id") != user_id])
        print("Account deleted.")


def manage_users(role):
    while True:
        choices = [
            "View All",
            "Add Trainer" if role == "trainer" else "Edit Trainee",
            "Edit Trainer" if role == "trainer" else "Delete Trainee",
        ]

        if role == "trainer":
            choices.append("Delete Trainer")

        choices.append("Back")
        choice = arrow_menu(f"MANAGE {role.upper()}S", choices)

        if not choice or choice == "Back":
            return

        if choice == "View All":
            view_users(role)
        elif choice == "Add Trainer":
            create_trainer_account()
        elif choice.startswith("Edit"):
            edit_user(role)
        elif choice.startswith("Delete"):
            delete_user(role)

        input("\nPress Enter to continue...")


# ==================== COURSES ====================

def view_courses():
    courses = load_data("courses.json")

    if not courses:
        print("No courses found.")
        return

    for c in courses:
        print(
            f"\nID: {c.get('id')} | {c.get('title')}\n"
            f"Description: {c.get('description', '')}\n"
            f"Trainer: {c.get('trainer', 'Not assigned')}\n"
            f"Duration: {c.get('duration', '')}\n"
            f"Price: {c.get('price', 0)} SAR"
        )


def add_course():
    courses = load_data("courses.json")

    title = input("Course title: ").strip()
    description = input("Description: ").strip()
    duration = input("Duration: ").strip()

    if not title or not description or not duration:
        print("All fields are required.")
        return

    try:
        price = float(input("Price (SAR): "))
        if price < 0:
            raise ValueError
    except ValueError:
        print("Invalid price.")
        return

    courses.append({
        "id": next_id(courses),
        "title": title,
        "description": description,
        "trainer": "Not assigned",
        "trainer_id": None,
        "duration": duration,
        "price": price,
    })

    save_data("courses.json", courses)
    print("Course added.")


def edit_course():
    courses = load_data("courses.json")
    course = select_record("EDIT COURSE", courses, lambda c: c.get("title", ""))

    if not course:
        return

    course["title"] = get_value("Title", course.get("title", ""))
    course["description"] = get_value(
        "Description", course.get("description", "")
    )
    course["duration"] = get_value(
        "Duration", course.get("duration", "")
    )

    try:
        price = input(f"Price [{course.get('price', 0)}]: ").strip()
        if price:
            price = float(price)
            if price < 0:
                raise ValueError
            course["price"] = price
    except ValueError:
        print("Invalid price.")
        return

    save_data("courses.json", courses)
    print("Course updated.")


def delete_course():
    courses = load_data("courses.json")
    course = select_record("DELETE COURSE", courses, lambda c: c.get("title", ""))

    if not course:
        return

    course_id = course["id"]

    for filename in (
        "enrollments.json",
        "attendance.json",
        "lessons.json",
        "grades.json",
        "progress.json",
        "lesson_progress.json",
    ):
        records = load_data(filename)

        if any(r.get("course_id") == course_id for r in records):
            print(f"Related records exist in {filename}.")
            print("Course was not deleted.")
            return

    if confirm(f"Delete course {course.get('title')}?"):
        save_data(
            "courses.json",
            [c for c in courses if c.get("id") != course_id]
        )
        print("Course deleted.")


def manage_courses():
    while True:
        choice = arrow_menu("MANAGE COURSES", [
            "View All Courses",
            "Add New Course",
            "Edit Course",
            "Delete Course",
            "Back",
        ])

        if not choice or choice == "Back":
            return
        elif choice == "View All Courses":
            view_courses()
        elif choice == "Add New Course":
            add_course()
        elif choice == "Edit Course":
            edit_course()
        elif choice == "Delete Course":
            delete_course()

        input("\nPress Enter to continue...")


# ==================== LESSONS ====================

def view_lessons():
    lessons = load_data("lessons.json")
    courses = load_data("courses.json")

    for course in courses:
        print(f"\nCourse: {course.get('title')}")

        items = sorted(
            [
                l for l in lessons
                if l.get("course_id") == course.get("id")
            ],
            key=lambda l: l.get("order", 0)
        )

        if not items:
            print("No lessons.")
            continue

        for lesson in items:
            print(
                f"\nID: {lesson.get('id')} | Order: {lesson.get('order')}\n"
                f"Title: {lesson.get('title')}\n"
                f"Description: {lesson.get('description', '')}"
            )


def choose_course():
    return select_record(
        "CHOOSE COURSE",
        load_data("courses.json"),
        lambda c: c.get("title", "")
    )


def add_lesson():
    lessons = load_data("lessons.json")
    course = choose_course()

    if not course:
        return

    title = input("Lesson title: ").strip()
    description = input("Description: ").strip()

    if not title:
        print("Title is required.")
        return

    orders = [
        l.get("order", 0) for l in lessons
        if l.get("course_id") == course["id"]
    ]

    lessons.append({
        "id": next_id(lessons),
        "course_id": course["id"],
        "title": title,
        "description": description,
        "order": max(orders, default=0) + 1,
    })

    save_data("lessons.json", lessons)
    print("Lesson added.")


def edit_lesson():
    lessons = load_data("lessons.json")
    lesson = select_record("EDIT LESSON", lessons, lambda l: l.get("title", ""))

    if not lesson:
        return

    lesson["title"] = get_value("Title", lesson.get("title", ""))
    lesson["description"] = get_value(
        "Description", lesson.get("description", "")
    )

    try:
        order = input(f"Order [{lesson.get('order', 1)}]: ").strip()
        if order:
            order = int(order)
            if order < 1:
                raise ValueError
            lesson["order"] = order
    except ValueError:
        print("Invalid order.")
        return

    if confirm("Change course?"):
        course = choose_course()
        if course:
            lesson["course_id"] = course["id"]

    save_data("lessons.json", lessons)
    print("Lesson updated.")


def delete_lesson():
    lessons = load_data("lessons.json")
    lesson = select_record("DELETE LESSON", lessons, lambda l: l.get("title", ""))

    if not lesson:
        return

    if confirm(f"Delete lesson {lesson.get('title')}?"):
        save_data(
            "lessons.json",
            [l for l in lessons if l.get("id") != lesson["id"]]
        )
        print("Lesson deleted.")


def manage_lessons():
    while True:
        choice = arrow_menu("MANAGE LESSONS", [
            "View All Lessons",
            "Add New Lesson",
            "Edit Lesson",
            "Delete Lesson",
            "Back",
        ])

        if not choice or choice == "Back":
            return
        elif choice == "View All Lessons":
            view_lessons()
        elif choice == "Add New Lesson":
            add_lesson()
        elif choice == "Edit Lesson":
            edit_lesson()
        elif choice == "Delete Lesson":
            delete_lesson()

        input("\nPress Enter to continue...")


# ==================== ASSIGN TRAINER ====================

def assign_trainer_to_course():
    courses = load_data("courses.json")
    trainers = [u for u in load_users() if u.get("role") == "trainer"]

    course = select_record("CHOOSE COURSE", courses, lambda c: c.get("title", ""))
    if not course:
        return

    trainer = select_record(
        "CHOOSE TRAINER",
        trainers,
        lambda t: f"{t.get('full_name')} ({t.get('email')})"
    )
    if not trainer:
        return

    course["trainer_id"] = trainer["id"]
    course["trainer"] = trainer["full_name"]

    save_data("courses.json", courses)
    print("Trainer assigned successfully.")


# ==================== REPORTS ====================

def view_enrollments():
    enrollments = load_data("enrollments.json")
    users = load_users()
    courses = load_data("courses.json")

    if not enrollments:
        print("No enrollments found.")
        return

    for item in enrollments:
        trainee = next(
            (u for u in users if u.get("id") == item.get("user_id")),
            None
        )
        course = next(
            (c for c in courses if c.get("id") == item.get("course_id")),
            None
        )

        print(
            f"\nTrainee: {trainee.get('full_name') if trainee else 'Unknown'}\n"
            f"Course: {course.get('title') if course else 'Unknown'}\n"
            f"Date: {item.get('date', '')}\n"
            f"Status: {item.get('status', '')}"
        )


def view_attendance_reports():
    records = load_data("attendance.json")
    users = load_users()
    courses = load_data("courses.json")

    if not records:
        print("No attendance records found.")
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

        print(
            f"\nTrainee: {trainee.get('full_name') if trainee else 'Unknown'}\n"
            f"Course: {course.get('title') if course else 'Unknown'}\n"
            f"Date: {record.get('date', '')}\n"
            f"Status: {record.get('status', '')}"
        )


# ==================== ADMIN DASHBOARD ====================

def admin_page(user):
    while True:
        choice = arrow_menu("ADMIN DASHBOARD", [
            "Manage Trainers",
            "Manage Trainees",
            "Manage Courses",
            "Manage Lessons",
            "Assign Trainer to Course",
            "View Enrollments",
            "View Attendance Reports",
            "Create Trainer Account",
            "Back to Main Menu",
            "Log Out",
        ])

        if not choice or choice == "Log Out":
            print("You have logged out successfully.")
            return "logout"

        elif choice == "Manage Trainers":
            manage_users("trainer")
        elif choice == "Manage Trainees":
            manage_users("trainee")
        elif choice == "Manage Courses":
            manage_courses()
        elif choice == "Manage Lessons":
            manage_lessons()
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