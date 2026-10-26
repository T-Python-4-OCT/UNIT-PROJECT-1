import json
import os


USERS_FILE = os.path.join("data", "users.json")
COURSES_FILE = os.path.join("data", "courses.json")


def load_data(file_path):
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def view_trainers():
    users = load_data(USERS_FILE)
    courses = load_data(COURSES_FILE)

    trainers = []

    for user in users:
        if user.get("role") == "trainer":
            trainer_courses = []

            for course in courses:
                course_trainer_id = course.get("trainer_id")
                course_trainer_name = course.get("trainer", "").strip().lower()

                if (
                    course_trainer_id == user.get("id")
                    or (
                        course_trainer_id is None
                        and course_trainer_name == user.get("full_name", "").strip().lower()
                    )
                ):
                    trainer_courses.append(course.get("title", "Unknown Course"))

            trainers.append({
                "id": user.get("id", "N/A"),
                "name": user.get("full_name", "N/A"),
                "email": user.get("email", "N/A"),
                "courses": trainer_courses
            })

    print("\n" + "=" * 115)
    print("TRAINERS LIST".center(115))
    print("=" * 115)

    if not trainers:
        print("\nNo trainers are registered.")
        return

    headers = ["ID", "Trainer Name", "Email", "Courses / Subjects"]
    widths = [8, 25, 30, 45]

    print(" | ".join(
        headers[index].ljust(widths[index])
        for index in range(len(headers))
    ))

    print("-" * 115)

    for trainer in trainers:
        subjects = ", ".join(trainer["courses"]) or "No courses assigned"

        row = [
            str(trainer["id"]),
            trainer["name"],
            trainer["email"],
            subjects
        ]

        print(" | ".join(
            row[index][:widths[index]].ljust(widths[index])
            for index in range(len(row))
        ))

    print("=" * 115)
    print(f"Total Trainers: {len(trainers)}")
