"""Service module for managing university subjects."""

from rich.table import Table
from models.classes import Subject
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    prompt_required_text,
    prompt_positive_int,
    prompt_select,
    prompt_confirm,
    show_spinner
)


def manage_subjects_menu(data):
    """Main submenu for subject management."""
    while True:
        print_header(
            "SECTION: Subject Management",
            "View, add, edit, or delete your registered university courses"
        )
        choices = [
            "1. View All Subjects",
            "2. Add New Subject",
            "3. Edit Subject",
            "4. Delete Subject",
            "5. Back to Main Menu"
        ]
        choice = prompt_select("Select an action from Subject Management:", choices)

        if choice is None or "5." in choice:
            break
        elif "1." in choice:
            view_all_subjects(data)
        elif "2." in choice:
            add_subject(data)
        elif "3." in choice:
            edit_subject(data)
        elif "4." in choice:
            delete_subject(data)


def display_subjects_table(subjects, table_title="Registered University Subjects"):
    """Display subjects in a formatted rich table."""
    if len(subjects) == 0:
        print_info("No subjects available to display.")
        return

    table = Table(title=f"{table_title} (Total: {len(subjects)})", show_header=True, header_style="bold cyan")
    table.add_column("Subject ID", width=12)
    table.add_column("Course Code", width=14)
    table.add_column("Subject Name", width=32)
    table.add_column("Instructor", width=24)
    table.add_column("Credit Hours", justify="center", width=14)

    for s in subjects:
        table.add_row(
            s.subject_id,
            s.code,
            s.name,
            s.instructor,
            str(s.credit_hours)
        )

    console.print()
    console.print(table)


def view_all_subjects(data):
    """Display all registered subjects."""
    print_header("VIEW: All Registered Subjects", "Complete list of your current semester courses")
    show_spinner("Loading subjects...")
    display_subjects_table(data["subjects"], "All Registered University Subjects")


def generate_next_subject_id(subjects):
    """Generate next sequential ID for subjects (e.g., SUB-001)."""
    max_num = 0
    for item in subjects:
        if item.subject_id.startswith("SUB-"):
            num_part = item.subject_id.replace("SUB-", "")
            if num_part.isdigit():
                num = int(num_part)
                if num > max_num:
                    max_num = num
    return f"SUB-{max_num + 1:03d}"


def add_subject(data):
    """Add a new subject to the dataset."""
    print_header("ACTION: Add New Subject", "Enter the details for the new university course")
    code = prompt_required_text("Enter Course Code (e.g., CS101):")
    if code is None:
        return

    for existing in data["subjects"]:
        if existing.code.lower() == code.lower():
            print_error(f"A subject with code '{code.upper()}' already exists.")
            return

    name = prompt_required_text("Enter Subject Name (e.g., Software Engineering):")
    if name is None:
        return

    instructor = prompt_required_text("Enter Instructor Name:")
    if instructor is None:
        return

    hours = prompt_positive_int("Enter Credit Hours:", default_value="3")
    if hours is None:
        return

    new_id = generate_next_subject_id(data["subjects"])
    new_subject = Subject(new_id, name, code, instructor, hours)

    show_spinner("Saving new subject...")
    data["subjects"].append(new_subject)
    save_data(data)
    print_success(f"Subject '{new_subject.code} - {new_subject.name}' added successfully.")


def choose_subject(subjects, prompt_text="Select a Subject:"):
    """Helper to select a subject interactively."""
    if len(subjects) == 0:
        print_info("No subjects available.")
        return None

    choices = []
    for s in subjects:
        choices.append(f"[{s.subject_id}] {s.code} - {s.name}")
    choices.append("Cancel")

    selected = prompt_select(prompt_text, choices)
    if selected is None or selected == "Cancel":
        return None

    for s in subjects:
        if f"[{s.subject_id}]" in selected:
            return s
    return None


def edit_subject(data):
    """Edit an existing subject's details."""
    print_header("ACTION: Edit Subject", "Select a course to update its details")
    subject = choose_subject(data["subjects"], "Select the subject you want to edit:")
    if subject is None:
        return

    new_code = prompt_required_text("Course Code:", default_value=subject.code)
    if new_code is None:
        return

    new_name = prompt_required_text("Subject Name:", default_value=subject.name)
    if new_name is None:
        return

    new_instructor = prompt_required_text("Instructor Name:", default_value=subject.instructor)
    if new_instructor is None:
        return

    new_hours = prompt_positive_int("Credit Hours:", default_value=str(subject.credit_hours))
    if new_hours is None:
        return

    subject.code = new_code.upper()
    subject.name = new_name
    subject.instructor = new_instructor
    subject.credit_hours = new_hours

    show_spinner("Updating subject...")
    save_data(data)
    print_success(f"Subject '{subject.code}' updated successfully.")


def delete_subject(data):
    """Delete a subject if not linked to tasks."""
    print_header("ACTION: Delete Subject", "Remove a subject if it has no linked items")
    subject = choose_subject(data["subjects"], "Select the subject to delete:")
    if subject is None:
        return

    linked_tasks = sum(1 for t in data["tasks"] if t.subject_id == subject.subject_id)
    linked_exams = sum(1 for e in data["exams"] if e.subject_id == subject.subject_id)

    if linked_tasks > 0 or linked_exams > 0:
        print_warning(
            f"Cannot delete '{subject.code}'. It is linked to {linked_tasks} task(s) and {linked_exams} exam(s)."
        )
        return

    if prompt_confirm(f"Are you sure you want to delete '{subject.code} - {subject.name}'?"):
        data["subjects"].remove(subject)
        save_data(data)
        print_success("Subject deleted successfully.")