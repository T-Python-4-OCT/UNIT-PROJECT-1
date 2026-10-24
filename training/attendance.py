import json
import os
from datetime import date

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")


def mark_attendance(trainer):
    with open(os.path.join(DATA_FOLDER, "courses.json"), encoding="utf-8") as f:
        courses = json.load(f)

    with open(os.path.join(DATA_FOLDER, "enrollments.json"), encoding="utf-8") as f:
        enrollments = json.load(f)

    with open(os.path.join(DATA_FOLDER, "users.json"), encoding="utf-8") as f:
        users = json.load(f)

    courses = [c for c in courses if c.get("trainer_id") == trainer["id"]]
    if not courses:
        print("No courses assigned.")
        return

    for c in courses:
        print(c["id"], c["title"])

    course_id = int(input("Course ID: "))
    if not any(c["id"] == course_id for c in courses):
        print("Invalid course.")
        return

    trainees = [e for e in enrollments if e["course_id"] == course_id and e.get("status") == "enrolled"]
    trainees = [u for u in users if u["id"] in [e["user_id"] for e in trainees] and u.get("role") == "trainee"]

    for t in trainees:
        print(t["id"], t["full_name"])

    trainee_id = int(input("Trainee ID: "))
    if not any(t["id"] == trainee_id for t in trainees):
        print("Invalid trainee.")
        return

    status = input("Present or Absent: ").strip().title()
    if status not in ["Present", "Absent"]:
        print("Invalid status.")
        return

    path = os.path.join(DATA_FOLDER, "attendance.json")
    records = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []

    if any(r["course_id"] == course_id and r["trainee_id"] == trainee_id and r["date"] == str(date.today()) for r in records):
        print("Attendance already recorded today.")
        return

    records.append({"course_id": course_id, "trainee_id": trainee_id, "date": str(date.today()), "status": status})

    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    print("Attendance saved.")
