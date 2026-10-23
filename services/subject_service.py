from faker import Faker
from rich.table import Table
from models.classes import Subject
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_required_text,
    prompt_positive_int,
    prompt_select,
    prompt_confirm,
    show_spinner
)

fake = Faker()

def manage_subjects_menu(data):
    while True:
        print_header(
            "SECTION: Subject Management",
            "View, add, or delete your academic courses"
        )
        choices = [
            "1. View All Subjects",
            "2. Add New Subject (Manual or Auto-Faker)",
            "3. Delete Subject",
            "4. Back to Main Menu"
        ]
        choice = prompt_select("Select an action:", choices)

        if choice is None or "4." in choice:
            break
        elif "1." in choice:
            view_all_subjects(data)
        elif "2." in choice:
            add_subject(data)
        elif "3." in choice:
            delete_subject(data)

def view_all_subjects(data):
    print_header("VIEW: All Subjects", "List of registered courses")
    show_spinner("Loading subjects...")
    subjects = data["subjects"]

    if not subjects:
        print_info("No subjects registered yet.")
        return

    table = Table(title=f"Registered Courses (Total: {len(subjects)})", show_header=True, header_style="bold cyan")
    table.add_column("ID", width=10)
    table.add_column("Code", width=10)
    table.add_column("Name", width=30)
    table.add_column("Instructor", width=22)
    table.add_column("Credit Hours", width=12)

    for s in subjects:
        table.add_row(s.subject_id, s.code, s.name, s.instructor, str(s.credit_hours))

    console.print()
    console.print(table)

def generate_next_subject_id(subjects):
    max_num = 0
    for s in subjects:
        if s.subject_id.startswith("SUB-"):
            num_part = s.subject_id.replace("SUB-", "")
            if num_part.isdigit():
                num = int(num_part)
                if num > max_num:
                    max_num = num
    return f"SUB-{max_num + 1:03d}"

def add_subject(data):
    print_header("ACTION: Add New Subject", "Register a new course")
    
    mode = prompt_select(
        "How would you like to add the subject?",
        ["1. Auto-generate completely with Faker", "2. Enter manually (with Faker defaults)"]
    )
    if not mode:
        return

    if "1." in mode:
        name = fake.catch_phrase().title()
        code = fake.bothify(text="???###").upper()
        instructor = f"Dr. {fake.name()}"
        credit_hours = fake.random_int(min=2, max=4)
    else:
        name = prompt_required_text("Enter Subject Name:", default_value=fake.catch_phrase().title())
        code = prompt_required_text("Enter Course Code:", default_value=fake.bothify(text="???###").upper()).upper()
        instructor = prompt_required_text("Enter Instructor Name:", default_value=f"Dr. {fake.name()}")
        credit_hours = prompt_positive_int("Enter Credit Hours:", default_value=str(fake.random_int(min=2, max=4)))

    for s in data["subjects"]:
        if s.code == code:
            print_error(f"Subject with code '{code}' already exists.")
            return

    new_id = generate_next_subject_id(data["subjects"])
    new_subject = Subject(new_id, name, code, instructor, credit_hours)

    show_spinner("Saving subject...")
    data["subjects"].append(new_subject)
    save_data(data)
    print_success(f"Subject '{name}' ({code}) with {instructor} added successfully.")

def delete_subject(data):
    print_header("ACTION: Delete Subject", "Remove an existing course")
    if not data["subjects"]:
        print_info("No subjects available to delete.")
        return

    choices = [f"[{s.subject_id}] {s.code} - {s.name}" for s in data["subjects"]]
    choices.append("Cancel")

    selected = prompt_select("Select subject to delete:", choices)
    if not selected or selected == "Cancel":
        return

    sub_id = selected.split("]")[0].replace("[", "").strip()

    linked_tasks = any(t.subject_id == sub_id for t in data.get("tasks", []))
    linked_projects = any(p.subject_id == sub_id for p in data.get("projects", []))
    linked_exams = any(e.subject_id == sub_id for e in data.get("exams", []))

    if linked_tasks or linked_projects or linked_exams:
        print_error("Cannot delete this subject because it has linked tasks, projects, or exams.")
        return

    if prompt_confirm("Are you sure you want to delete this subject?"):
        data["subjects"] = [s for s in data["subjects"] if s.subject_id != sub_id]
        save_data(data)
        print_success("Subject deleted successfully.")