import json
import os
from datetime import date

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")


def load_data(filename):
    path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(path):
        return []

    with open(path, encoding="utf-8") as file:
        return json.load(file)


def save_data(filename, data):
    path = os.path.join(DATA_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def mark_attendance(trainer):
    courses = load_data("courses.json")
    enrollments = load_data("enrollments.json")
    users = load_data("users.json")

    courses = [
        course for course in courses
        if course.get("trainer_id") == trainer["id"]
    ]

    if not courses:
        print("No courses assigned.")
        return

    for course in courses:
        print(course["id"], course["title"])

    try:
        course_id = int(input("Course ID: "))
    except ValueError:
        print("Invalid course ID.")
        return

    course = next(
        (course for course in courses if course["id"] == course_id),
        None
    )

    if course is None:
        print("Invalid course.")
        return

    enrolled_ids = [
        enrollment["user_id"]
        for enrollment in enrollments
        if enrollment["course_id"] == course_id
        and enrollment.get("status", "enrolled") == "enrolled"
    ]

    trainees = [
        user for user in users
        if user["id"] in enrolled_ids
        and user.get("role") == "trainee"
    ]

    if not trainees:
        print("No trainees enrolled in this course.")
        return

    for trainee in trainees:
        print(trainee["id"], trainee["full_name"])

    try:
        trainee_id = int(input("Trainee ID: "))
    except ValueError:
        print("Invalid trainee ID.")
        return

    if not any(trainee["id"] == trainee_id for trainee in trainees):
        print("Invalid trainee.")
        return

    status = input("Present or Absent: ").strip().title()

    if status not in ["Present", "Absent"]:
        print("Invalid status.")
        return

    records = load_data("attendance.json")
    today = str(date.today())

    if any(
        record["course_id"] == course_id
        and record["trainee_id"] == trainee_id
        and record["date"] == today
        for record in records
    ):
        print("Attendance already recorded today.")
        return

    records.append({
        "course_id": course_id,
        "trainee_id": trainee_id,
        "date": today,
        "status": status
    })

    save_data("attendance.json", records)

    print("Attendance saved.")


def view_my_attendance(user):
    records = load_data("attendance.json")
    courses = load_data("courses.json")
    enrollments = load_data("enrollments.json")

    course_ids = {
        enrollment["course_id"]
        for enrollment in enrollments
        if enrollment["user_id"] == user["id"]
        and enrollment.get("status", "enrolled") == "enrolled"
    }

    if not course_ids:
        print("You are not enrolled in any courses.")
        return

    rows = []

    for course in courses:
        if course["id"] not in course_ids:
            continue

        attendance = [
            record for record in records
            if record["course_id"] == course["id"]
            and record["trainee_id"] == user["id"]
        ]

        present = sum(
            record["status"] == "Present"
            for record in attendance
        )

        absent = sum(
            record["status"] == "Absent"
            for record in attendance
        )

        total_days = course.get("total_days", 0)

        percentage = (
            present / total_days * 100
            if total_days > 0
            else 0
        )

        rows.append([
            course["title"],
            total_days,
            present,
            absent,
            f"{percentage:.1f}%"
        ])

    headers = [
        "Course",
        "Total Days",
        "Present",
        "Absent",
        "Attendance Rate"
    ]

    widths = [
        max(len(str(row[index])) for row in [headers] + rows)
        for index in range(len(headers))
    ]

    border = "+" + "+".join(
        "-" * (width + 2)
        for width in widths
    ) + "+"

    print("\n" + border)

    for index, row in enumerate([headers] + rows):
        print(
            "|" + "|".join(
                " " + str(value).ljust(widths[i]) + " "
                for i, value in enumerate(row)
            ) + "|"
        )

        if index == 0:
            print(border)

    print(border)