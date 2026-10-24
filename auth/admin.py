import json
import os
import questionary

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
    name = questionary.text("Enter trainer full name:").ask()
    email = questionary.text("Enter trainer email:").ask()

    if not name or not name.strip() or not email or not email.strip():
        print("\nName and email are required.")
        return

    email = email.strip().lower()

    if any(u.get("email", "").lower() == email for u in users):
        print("\nThis email is already registered.")
        return

    password = questionary.password("Create trainer password:").ask()

    if password is None or len(password) < 8:
        print("\nPassword must be at least 8 characters.")
        return

    confirm = questionary.password("Confirm trainer password:").ask()

    if password != confirm:
        print("\nPasswords do not match.")
        return

    trainer = {
        "id": max((u.get("id", 0) for u in users), default=0) + 1,
        "full_name": name.strip(),
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

    course_choice = questionary.select(
        "Choose a course:",
        choices=[
            f"{c['id']}. {c['title']} (Trainer: {c.get('trainer', 'Not assigned')})"
            for c in courses
        ]
    ).ask()

    if course_choice is None:
        return

    course_id = int(course_choice.split(".", 1)[0])
    course = next(c for c in courses if c.get("id") == course_id)

    trainer_choice = questionary.select(
        "Choose a trainer:",
        choices=[f"{t['id']}. {t['full_name']} ({t['email']})" for t in trainers]
    ).ask()

    if trainer_choice is None:
        return

    trainer_id = int(trainer_choice.split(".", 1)[0])
    trainer = next(t for t in trainers if t.get("id") == trainer_id)

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
        trainee = next(
            (u for u in users if u.get("id") == record.get("user_id")),
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


def admin_page(user):
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

    while True:
        print(f"\n{'=' * 40}\nADMIN DASHBOARD\n{'=' * 40}")
        print(f"Welcome, {user.full_name}!")

        choice = questionary.select(
            "Choose an option:", choices=choices
        ).ask()

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