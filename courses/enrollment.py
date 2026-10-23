import json
import os
from datetime import date


DATA_FOLDER = "data"
COURSES_FILE = os.path.join(DATA_FOLDER, "courses.json")
ENROLLMENTS_FILE = os.path.join(DATA_FOLDER, "enrollments.json")


def load_data(file_path):
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(file_path, data):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def enroll_in_course(user):
    courses = load_data(COURSES_FILE)
    enrollments = load_data(ENROLLMENTS_FILE)

    if not courses:
        print("\nNo courses are available.")
        return

    print("\n" + "=" * 60)
    print("ENROLL IN A COURSE")
    print("=" * 60)

    for course in courses:
        print(
            f"ID: {course.get('id')} | "
            f"Title: {course.get('title', 'N/A')} | "
            f"Price: {course.get('price', 'N/A')} SAR"
        )

    try:
        course_id = int(input("\nEnter Course ID: ").strip())
    except ValueError:
        print("\nPlease enter a valid course ID.")
        return

    course = next(
        (item for item in courses if item.get("id") == course_id),
        None
    )

    if course is None:
        print("\nCourse not found.")
        return

    user_id = user["id"]

    for enrollment in enrollments:
        if (
            enrollment.get("user_id") == user_id
            and enrollment.get("course_id") == course_id
            and enrollment.get("status", "enrolled") == "enrolled"
        ):
            print("\nYou are already enrolled in this course.")
            return

    enrollments.append({
        "user_id": user_id,
        "course_id": course_id,
        "enrollment_date": date.today().isoformat(),
        "status": "enrolled"
    })

    save_data(ENROLLMENTS_FILE, enrollments)

    print(f"\nSuccessfully enrolled in {course.get('title', 'the course')}!")
