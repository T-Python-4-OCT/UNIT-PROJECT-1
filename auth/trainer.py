import json
import os
from datetime import date

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

from training.attendance import mark_attendance


BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")

USERS_FILE = os.path.join(DATA_FOLDER, "users.json")
COURSES_FILE = os.path.join(DATA_FOLDER, "courses.json")
ENROLLMENTS_FILE = os.path.join(DATA_FOLDER, "enrollments.json")
GRADES_FILE = os.path.join(DATA_FOLDER, "grades.json")

choices = [
    "View My Courses",
    "View My Trainees",
    "View Trainee Details",
    "Mark Attendance",
    "Manage Trainee Grades",
    "Log Out",
]

selected = 0


def load_data(file_path):
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


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
    event.app.invalidate()


@bindings.add("down")
def move_down(event):
    global selected
    selected = (selected + 1) % len(choices)
    event.app.invalidate()


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

    return [
        course for course in courses
        if (
            course.get("trainer_id") == trainer_id
            if course.get("trainer_id") is not None
            else course.get("trainer", "").strip().lower() == trainer_name
        )
    ]


def get_my_trainees(trainer):
    users = load_data(USERS_FILE)
    enrollments = load_data(ENROLLMENTS_FILE)
    courses = get_trainer_courses(trainer)
    course_ids = [course["id"] for course in courses if "id" in course]
    users_by_id = {
        user["id"]: user for user in users
        if "id" in user and user.get("role") == "trainee"
    }
    trainees = {}

    for enrollment in enrollments:
        user_id = enrollment.get("user_id")
        course_id = enrollment.get("course_id")

        if (
            course_id not in course_ids
            or enrollment.get("status", "enrolled") != "enrolled"
        ):
            continue

        user = users_by_id.get(user_id)

        if user is None:
            continue

        if user_id not in trainees:
            trainees[user_id] = {
                "id": user_id,
                "full_name": user.get("full_name", ""),
                "email": user.get("email", ""),
                "courses": [],
            }

        title = next(
            (
                course["title"]
                for course in courses
                if course["id"] == course_id
            ),
            "Unknown Course",
        )

        if title not in trainees[user_id]["courses"]:
            trainees[user_id]["courses"].append(title)

    return list(trainees.values())


def print_table(headers, rows):
    if not rows:
        print("\nNo data to display.")
        return

    widths = [
        max(len(str(row[i])) for row in [headers] + rows)
        for i in range(len(headers))
    ]

    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(border)

    for row in [headers] + rows:
        print(
            "|"
            + "|".join(
                " " + str(value).ljust(widths[i]) + " "
                for i, value in enumerate(row)
            )
            + "|"
        )

        if row == headers:
            print(border)

    print(border)


def view_my_courses(trainer):
    courses = get_trainer_courses(trainer)

    print("\n" + "=" * 70)
    print("MY COURSES")
    print("=" * 70)

    rows = [
        [
            course.get("id", ""),
            course.get("title", ""),
            course.get("duration", ""),
            course.get("price", ""),
        ]
        for course in courses
    ]

    if not rows:
        print("\nNo courses have been assigned to you.")
        return

    print_table(["ID", "Course Title", "Duration", "Price (SAR)"], rows)
    print(f"\nTotal Courses: {len(courses)}")


def view_my_trainees(trainer):
    trainees = get_my_trainees(trainer)

    print("\n" + "=" * 90)
    print("MY TRAINEES")
    print("=" * 90)

    rows = [
        [
            trainee["id"],
            trainee["full_name"],
            trainee["email"],
            ", ".join(trainee["courses"]),
        ]
        for trainee in trainees
    ]

    if not rows:
        print("\nNo trainees are enrolled in your courses.")
        return

    print_table(["ID", "Trainee Name", "Email", "Courses"], rows)
    print(f"\nTotal Trainees: {len(trainees)}")


def view_trainee_details(trainer):
    trainees = get_my_trainees(trainer)

    if not trainees:
        print("\nNo trainees are enrolled in your courses.")
        return

    try:
        trainee_id = int(input("\nEnter Trainee ID: "))
    except ValueError:
        print("\nPlease enter a valid numeric ID.")
        return

    trainee = next(
        (item for item in trainees if item["id"] == trainee_id),
        None,
    )

    if trainee is None:
        print("\nTrainee not found in your courses.")
        return

    print(f"\nID: {trainee['id']}")
    print(f"Name: {trainee['full_name']}")
    print(f"Email: {trainee['email']}")
    print("\nEnrolled Courses:")

    for course in trainee["courses"]:
        print(f"- {course}")


def manage_trainee_grades(trainer):
    courses = get_trainer_courses(trainer)

    if not courses:
        print("\nNo courses have been assigned to you.")
        return

    print("\nMY COURSES")

    for course in courses:
        print(f"{course['id']}. {course.get('title', 'Untitled Course')}")

    try:
        course_id = int(input("\nEnter Course ID: "))
    except ValueError:
        print("\nPlease enter a valid numeric ID.")
        return

    course = next(
        (item for item in courses if item.get("id") == course_id),
        None,
    )

    if course is None:
        print("\nCourse not found.")
        return

    enrollments = load_data(ENROLLMENTS_FILE)
    users = load_data(USERS_FILE)

    enrolled_ids = [
        item.get("user_id")
        for item in enrollments
        if item.get("course_id") == course_id
        and item.get("status", "enrolled") == "enrolled"
    ]

    trainees = [
        user for user in users
        if user.get("role") == "trainee"
        and user.get("id") in enrolled_ids
    ]

    if not trainees:
        print("\nNo trainees are enrolled in this course.")
        return

    print(f"\nTrainees in {course.get('title', '')}")

    for trainee in trainees:
        print(f"{trainee['id']}. {trainee.get('full_name', 'Unknown')}")

    try:
        trainee_id = int(input("\nEnter Trainee ID: "))
    except ValueError:
        print("\nPlease enter a valid numeric ID.")
        return

    trainee = next(
        (item for item in trainees if item.get("id") == trainee_id),
        None,
    )

    if trainee is None:
        print("\nTrainee not found in this course.")
        return

    assessment_name = input("\nEnter assessment name: ").strip()

    if not assessment_name:
        print("\nAssessment name cannot be empty.")
        return

    try:
        score = float(input("Enter trainee score: "))
        maximum_score = float(input("Enter maximum score: "))
    except ValueError:
        print("\nPlease enter valid numbers.")
        return

    if maximum_score <= 0 or score < 0 or score > maximum_score:
        print("\nThe score must be between 0 and the maximum score.")
        return

    grades = load_data(GRADES_FILE)

    existing_grade = next(
        (
            grade for grade in grades
            if grade.get("course_id") == course_id
            and grade.get("trainee_id") == trainee_id
            and grade.get("assessment_name", "").strip().lower()
            == assessment_name.lower()
        ),
        None,
    )

    if existing_grade:
        update = input(
            "\nThis assessment already has a grade. Update it? (y/n): "
        ).strip().lower()

        if update != "y":
            print("\nGrade was not changed.")
            return

        existing_grade["score"] = score
        existing_grade["maximum_score"] = maximum_score
        existing_grade["percentage"] = round(
            score / maximum_score * 100, 2
        )
        existing_grade["updated_at"] = date.today().isoformat()
        existing_grade["trainer_id"] = trainer.get("id")

    else:
        next_id = max(
            (grade.get("id", 0) for grade in grades),
            default=0,
        ) + 1

        grades.append({
            "id": next_id,
            "course_id": course_id,
            "course_title": course.get("title", ""),
            "trainee_id": trainee_id,
            "trainee_name": trainee.get("full_name", ""),
            "assessment_name": assessment_name,
            "score": score,
            "maximum_score": maximum_score,
            "percentage": round(score / maximum_score * 100, 2),
            "trainer_id": trainer.get("id"),
            "date": date.today().isoformat(),
        })

    save_data(GRADES_FILE, grades)

    print("\nGrade saved successfully.")
    print(f"Trainee: {trainee.get('full_name', '')}")
    print(f"Assessment: {assessment_name}")
    print(f"Score: {score:g} / {maximum_score:g}")
    print(f"Percentage: {score / maximum_score * 100:.2f}%")


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
        elif choice == "Mark Attendance":
            mark_attendance(trainer)
        elif choice == "Manage Trainee Grades":
            manage_trainee_grades(trainer)
        elif choice == "Log Out" or choice is None:
            print(f"\nGoodbye, {trainer['full_name']}!")
            print("You have logged out successfully.")
            return "logout"

        input("\nPress Enter to continue...")