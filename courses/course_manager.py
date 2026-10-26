import json
import os

COURSES_FILE = os.path.join("data", "courses.json")


def browse_courses():
    if not os.path.exists(COURSES_FILE):
        print("\nCourses file was not found.")
        return

    with open(COURSES_FILE, "r", encoding="utf-8") as file:
        courses = json.load(file)

    print("\n" + "=" * 115)
    print("AVAILABLE TRAINING COURSES".center(115))
    print("=" * 115)

    if not courses:
        print("\nNo courses are available.")
        return

    headers = ["ID", "Title", "Trainer", "Duration", "Price (SAR)"]
    rows = []

    for course in courses:
        rows.append([
            str(course.get("id", "N/A")),
            str(course.get("title", "N/A")),
            str(course.get("trainer", "N/A")),
            str(course.get("duration", "N/A")),
            str(course.get("price", "N/A"))
        ])

    widths = [5, 38, 25, 12, 15]

    header_line = " | ".join(
        headers[i].ljust(widths[i]) for i in range(len(headers))
    )

    print(header_line)
    print("-" * len(header_line))

    for row in rows:
        print(" | ".join(
            row[i][:widths[i]].ljust(widths[i])
            for i in range(len(row))
        ))

    print("=" * 115)
    print(f"Total Courses: {len(courses)}")

## 2. تعديل ملف `courses/course_search.py`

import json
import os

COURSES_FILE = os.path.join("data", "courses.json")


def search_course():
    if not os.path.exists(COURSES_FILE):
        print("\nCourses file was not found.")
        return

    with open(COURSES_FILE, "r", encoding="utf-8") as file:
        courses = json.load(file)

    if not courses:
        print("\nNo courses are available.")
        return

    search_text = input("\nEnter the course title to search: ").strip().lower()

    if not search_text:
        print("\nPlease enter a course title.")
        return

    found_courses = []

    for course in courses:
        title = course.get("title", "")

        if search_text in title.lower():
            found_courses.append(course)

    if not found_courses:
        print("\nNo matching courses were found.")
        return

    headers = ["ID", "Title", "Trainer", "Duration", "Price (SAR)"]
    widths = [5, 38, 25, 12, 15]

    print("\n" + "=" * 115)
    print("COURSE SEARCH RESULTS".center(115))
    print("=" * 115)

    header_line = " | ".join(
        headers[i].ljust(widths[i]) for i in range(len(headers))
    )

    print(header_line)
    print("-" * len(header_line))

    for course in found_courses:
        row = [
            str(course.get("id", "N/A")),
            str(course.get("title", "N/A")),
            str(course.get("trainer", "N/A")),
            str(course.get("duration", "N/A")),
            str(course.get("price", "N/A"))
        ]

        print(" | ".join(
            row[i][:widths[i]].ljust(widths[i])
            for i in range(len(row))
        ))

    print("=" * 115)
    print(f"Matching Courses: {len(found_courses)}")
