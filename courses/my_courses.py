from utils.json_manager import load_data


def view_my_courses(user):
    courses = load_data("courses.json")
    enrollments = load_data("enrollments.json")

    my_courses = []

    for enrollment in enrollments:
        if enrollment.get("user_id") == user.get("id"):
            course = next(
                (
                    course for course in courses
                    if course.get("id") == enrollment.get("course_id")
                ),
                None
            )

            if course:
                my_courses.append((course, enrollment))

    print("\n" + "=" * 120)
    print("MY ENROLLED COURSES".center(120))
    print("=" * 120)

    if not my_courses:
        print("You are not enrolled in any courses.")
        input("\nPress Enter to return to the trainee menu...")
        return

    headers = [
        "ID", "Course Title", "Trainer", "Duration",
        "Price (SAR)", "Enrollment Date", "Status"
    ]

    rows = []

    for course, enrollment in my_courses:
        rows.append([
            str(course.get("id", "")),
            str(course.get("title", "")),
            str(course.get("trainer", "Not assigned")),
            str(course.get("duration", "")),
            str(course.get("price", 0)),
            str(enrollment.get("enrollment_date", "")),
            str(enrollment.get("status", "enrolled"))
        ])

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    def print_row(row):
        print(
            "| " + " | ".join(
                row[i].ljust(widths[i])
                for i in range(len(row))
            ) + " |"
        )

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    print(separator)
    print_row(headers)
    print(separator)

    for row in rows:
        print_row(row)

    print(separator)
    print(f"\nTotal Enrolled Courses: {len(my_courses)}")
    input("\nPress Enter to return to the trainee menu...")
