import json
import os

from InquirerPy import inquirer


BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")
PROGRESS_FILE = os.path.join(DATA_FOLDER, "lesson_progress.json")


def load_data(filename):
    file_path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        json.dump(progress, file, ensure_ascii=False, indent=4)


def get_completed_lessons(user_id, course_id):
    progress = load_data("lesson_progress.json")

    return [
        item.get("lesson_id")
        for item in progress
        if item.get("user_id") == user_id
        and item.get("course_id") == course_id
        and item.get("completed") is True
    ]


def get_my_courses(user):
    courses = load_data("courses.json")
    enrollments = load_data("enrollments.json")
    my_courses = []

    for enrollment in enrollments:
        if (
            enrollment.get("user_id") == user.get("id")
            and enrollment.get("status", "enrolled") == "enrolled"
        ):
            course_id = enrollment.get("course_id")

            course = next(
                (item for item in courses if item.get("id") == course_id),
                None
            )

            if course and course not in my_courses:
                my_courses.append(course)

    return my_courses


def mark_lesson_completed(user):
    courses = get_my_courses(user)

    if not courses:
        print("\nYou are not enrolled in any courses.")
        return

    selected_course = inquirer.select(
        message="Choose a course:",
        choices=[
            f"{course['id']}. {course['title']}"
            for course in courses
        ]
    ).execute()

    if selected_course is None:
        return

    course_id = int(selected_course.split(".", 1)[0])
    lessons = load_data("lessons.json")

    course_lessons = [
        lesson for lesson in lessons
        if lesson.get("course_id") == course_id
    ]

    course_lessons.sort(key=lambda lesson: lesson.get("order", 0))

    if not course_lessons:
        print("\nNo lessons have been added to this course yet.")
        return

    completed_ids = get_completed_lessons(user["id"], course_id)

    incomplete_lessons = [
        lesson for lesson in course_lessons
        if lesson.get("id") not in completed_ids
    ]

    if not incomplete_lessons:
        print("\nYou have completed all lessons in this course!")
        return

    selected_lesson = inquirer.select(
        message="Choose a lesson to mark as completed:",
        choices=[
            f"{lesson['id']}. {lesson['title']}"
            for lesson in incomplete_lessons
        ]
    ).execute()

    if selected_lesson is None:
        return

    lesson_id = int(selected_lesson.split(".", 1)[0])
    progress = load_data("lesson_progress.json")

    progress.append({
        "user_id": user["id"],
        "course_id": course_id,
        "lesson_id": lesson_id,
        "completed": True
    })

    save_progress(progress)

    print("\nLesson marked as completed successfully!")


def view_my_progress(user):
    courses = get_my_courses(user)
    lessons = load_data("lessons.json")

    print("\n" + "=" * 105)
    print("MY TRAINING PROGRESS".center(105))
    print("=" * 105)

    if not courses:
        print("\nYou are not enrolled in any courses.")
        return

    # Table header
    print(
        f"{'Course Name':<40}"
        f"{'Progress':<15}"
        f"{'Lessons':<12}"
        f"{'Status':<20}"
    )

    print("-" * 87)

    for course in courses:
        course_id = course.get("id")

        course_lessons = [
            lesson for lesson in lessons
            if lesson.get("course_id") == course_id
        ]

        course_lessons.sort(key=lambda lesson: lesson.get("order", 0))

        if not course_lessons:
            print(
                f"{course.get('title', 'Unknown Course'):<40}"
                f"{'N/A':<15}"
                f"{'0/0':<12}"
                f"{'No Lessons':<20}"
            )
            continue

        completed_ids = get_completed_lessons(
            user["id"],
            course_id
        )

        completed_count = sum(
            1
            for lesson in course_lessons
            if lesson.get("id") in completed_ids
        )

        total_lessons = len(course_lessons)

        percentage = completed_count / total_lessons * 100

        if completed_count == total_lessons:
            status = "Completed"
        elif completed_count > 0:
            status = "In Progress"
        else:
            status = "Not Started"

        lessons_progress = f"{completed_count}/{total_lessons}"

        print(
            f"{course.get('title', 'Unknown Course'):<40}"
            f"{percentage:>6.1f}%{'':<8}"
            f"{lessons_progress:<12}"
            f"{status:<20}"
        )

    print("-" * 87)
    print(f"Total Courses: {len(courses)}")
