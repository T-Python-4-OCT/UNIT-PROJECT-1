import json
import os

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from courses.course_manager import browse_courses
from courses.course_search import search_course
from courses.enrollment import enroll_in_course
from courses.my_courses import view_my_courses
from training.attendance import view_my_attendance
from training.lessons import view_my_progress, mark_lesson_completed


BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRADES_FILE = os.path.join(BASE_FOLDER, "data", "grades.json")


def load_grades():
    """Load grades from the JSON file."""

    if not os.path.exists(GRADES_FILE):
        return []

    try:
        with open(GRADES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def view_my_grades(user):
    """Display the logged-in trainee's grades in a table."""

    grades = [
        grade
        for grade in load_grades()
        if (
            grade.get("trainee_id") == user.get("id")
            or grade.get("user_id") == user.get("id")
        )
    ]

    print("\n" + "=" * 100)
    print("MY GRADES".center(100))
    print("=" * 100)

    if not grades:
        print("\nNo grades available yet.")
        print("\nPlease check whether the trainer has entered your grades.")
        return

    print(
        f"{'Course':<30}"
        f"{'Assessment':<25}"
        f"{'Score':<15}"
        f"{'Percentage':<15}"
        f"{'Status':<15}"
    )

    print("-" * 100)

    for grade in grades:
        course = grade.get("course_title", "N/A")
        assessment = grade.get(
            "assessment_name",
            grade.get("assessment", "N/A")
        )

        score_value = grade.get("score", grade.get("grade", "N/A"))
        maximum_score = grade.get(
            "maximum_score",
            grade.get("max_score")
        )

        if maximum_score is not None:
            score = f"{score_value}/{maximum_score}"
        else:
            score = str(score_value)

        percentage_value = grade.get("percentage")

        if percentage_value is None:
            try:
                if maximum_score and isinstance(
                    score_value, (int, float)
                ):
                    percentage_value = (
                        score_value / maximum_score
                    ) * 100
                else:
                    percentage_value = None
            except (TypeError, ZeroDivisionError):
                percentage_value = None

        if percentage_value is not None:
            percentage = f"{percentage_value}%"
        else:
            percentage = "N/A"

        status = grade.get("status", "N/A")

        print(
            f"{str(course):<30}"
            f"{str(assessment):<25}"
            f"{score:<15}"
            f"{percentage:<15}"
            f"{str(status):<15}"
        )

    print("-" * 100)
    print(f"Total Assessments: {len(grades)}")


def trainee_page(user):
    menu_items = [
        "View My Profile",
        "Browse Training Courses",
        "Search for a Course",
        "Enroll in a Course",
        "View My Courses",
        "View My Attendance",
        "Mark Lesson as Completed",
        "View My Progress",
        "View My Grades",
        "Back to Main Menu",
        "Log Out",
    ]

    selected_index = 0

    def get_menu():
        return [
            (
                "class:selected" if index == selected_index else "class:normal",
                f"  {'❯' if index == selected_index else ' '} {item}\n"
            )
            for index, item in enumerate(menu_items)
        ]

    bindings = KeyBindings()

    @bindings.add("up")
    def move_up(event):
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(menu_items)
        event.app.invalidate()

    @bindings.add("down")
    def move_down(event):
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(menu_items)
        event.app.invalidate()

    @bindings.add("enter")
    def select_item(event):
        event.app.exit(result=menu_items[selected_index])

    style = Style.from_dict({
        "selected": "bg:#008080 #ffffff bold",
        "normal": "#ffffff",
    })

    actions = {
        "Browse Training Courses": lambda: browse_courses(),
        "Search for a Course": lambda: search_course(),
        "Enroll in a Course": lambda: enroll_in_course(user),
        "View My Courses": lambda: view_my_courses(user),
        "View My Attendance": lambda: view_my_attendance(user),
        "Mark Lesson as Completed": lambda: mark_lesson_completed(user),
        "View My Progress": lambda: view_my_progress(user),
        "View My Grades": lambda: view_my_grades(user),
    }

    while True:
        print("\n" + "=" * 45)
        print("MOTQEN ACADEMY".center(45))
        print("TRAINEE PORTAL".center(45))
        print("=" * 45)
        print(f"\nWelcome, {user.get('full_name', 'Trainee')}!")

        application = Application(
            layout=Layout(
                HSplit([
                    Window(
                        FormattedTextControl(get_menu),
                        always_hide_cursor=True,
                    )
                ])
            ),
            key_bindings=bindings,
            style=style,
            full_screen=False,
            mouse_support=False,
        )

        choice = application.run()
        print()

        if choice == "View My Profile":
            print("\n" + "=" * 45)
            print("MY PROFILE".center(45))
            print("=" * 45)
            print(f"ID: {user.get('id', 'N/A')}")
            print(f"Name: {user.get('full_name', 'N/A')}")
            print(f"Email: {user.get('email', 'N/A')}")
            print(f"Role: {user.get('role', 'N/A')}")

        elif choice in actions:
            actions[choice]()

        elif choice == "Back to Main Menu":
            return "main_menu"

        elif choice == "Log Out":
            return "logout"

        input("\nPress Enter to return to the trainee menu...")