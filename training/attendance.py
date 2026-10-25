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


def mark_attendance(trainer):
    courses = load_data("courses.json")
    enrollments = load_data("enrollments.json")
    users = load_data("users.json")

    courses = [c for c in courses if c.get("trainer_id") == trainer["id"]]

    if not courses:
        print("No courses assigned.")
        return

    for c in courses:
        print(c["id"], c["title"])

    try:
        course_id = int(input("Course ID: "))
    except ValueError:
        print("Invalid course ID.")
        return

    if not any(c["id"] == course_id for c in courses):
        print("Invalid course.")
        return

    enrolled_ids = [
        e["user_id"] for e in enrollments
        if e["course_id"] == course_id
        and e.get("status", "enrolled") == "enrolled"
    ]

    trainees = [
        u for u in users
        if u["id"] in enrolled_ids and u.get("role") == "trainee"
    ]

    if not trainees:
        print("No trainees enrolled in this course.")
        return

    for t in trainees:
        print(t["id"], t["full_name"])

    try:
        trainee_id = int(input("Trainee ID: "))
    except ValueError:
        print("Invalid trainee ID.")
        return

    if not any(t["id"] == trainee_id for t in trainees):
        print("Invalid trainee.")
        return

    status = input("Present or Absent: ").strip().title()

    if status not in ["Present", "Absent"]:
        print("Invalid status.")
        return

    records = load_data("attendance.json")
    today = str(date.today())

    if any(
        r["course_id"] == course_id
        and r["trainee_id"] == trainee_id
        and r["date"] == today
        for r in records
    ):
        print("Attendance already recorded today.")
        return

    records.append({
        "course_id": course_id,
        "trainee_id": trainee_id,
        "date": today,
        "status": status
    })

    with open(
        os.path.join(DATA_FOLDER, "attendance.json"),
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

    print("Attendance saved.")


def view_my_attendance(user):
    records = load_data("attendance.json")
    courses = load_data("courses.json")
    enrollments = load_data("enrollments.json")

    course_ids = {
        e["course_id"] for e in enrollments
        if e["user_id"] == user["id"]
        and e.get("status", "enrolled") == "enrolled"
    }

    if not course_ids:
        print("You are not enrolled in any courses.")
        return

    rows = []

    for course in courses:
        if course["id"] not in course_ids:
            continue

        attendance = [
            r for r in records
            if r["course_id"] == course["id"]
            and r["trainee_id"] == user["id"]
        ]

        present = sum(r["status"] == "Present" for r in attendance)
        absent = sum(r["status"] == "Absent" for r in attendance)
        total = present + absent
        percentage = present / total * 100 if total else 0

        rows.append([
            course["title"],
            present,
            absent,
            f"{percentage:.1f}%"
        ])

    headers = ["Course", "Present", "Absent", "Attendance Rate"]
    widths = [
        max(len(str(row[i])) for row in [headers] + rows)
        for i in range(len(headers))
    ]

    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    print("\n" + border)

    for index, row in enumerate([headers] + rows):
        print("|" + "|".join(
            " " + str(value).ljust(widths[i]) + " "
            for i, value in enumerate(row)
        ) + "|")

        if index == 0:
            print(border)

    print(border)
