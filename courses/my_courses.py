import json
import os


DATA_FOLDER = "data"
COURSES_FILE = os.path.join(DATA_FOLDER, "courses.json")
ENROLLMENTS_FILE = os.path.join(DATA_FOLDER, "enrollments.json")


def load_data(file_path):
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def view_my_courses(user):
    courses = load_data(COURSES_FILE)
    enrollments = load_data(ENROLLMENTS_FILE)

    user_id = user["id"]

    my_courses = []

    for enrollment in enrollments:
        if (
            enrollment.get("user_id") == user_id
            and enrollment.get("status", "enrolled") == "enrolled"
        ):
            course_id = enrollment.get("course_id")

            for course in courses:
                if course.get("id") == course_id:
                    my_courses.append({
                        "course": course,
                        "enrollment_date": enrollment.get(
                            "enrollment_date",
                            enrollment.get("date", "N/A")
                        ),
                        "status": enrollment.get("status", "enrolled")
                    })
                    break

    print("\n" + "=" * 75)
    print("MY ENROLLED COURSES".center(75))
    print("=" * 75)

    if not my_courses:
        print("\nYou are not enrolled in any courses.")
        return

    for item in my_courses:
        course = item["course"]

        print(f"\nCourse ID: {course.get('id', 'N/A')}")
        print(f"Title: {course.get('title', 'N/A')}")
        print(f"Trainer: {course.get('trainer', 'N/A')}")
        print(f"Duration: {course.get('duration', 'N/A')}")
        print(f"Price: {course.get('price', 'N/A')} SAR")
        print(f"Enrollment Date: {item['enrollment_date']}")
        print(f"Status: {item['status']}")
        print("-" * 75)

    print(f"\nTotal Enrolled Courses: {len(my_courses)}")