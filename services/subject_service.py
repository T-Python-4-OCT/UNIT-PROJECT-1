"""
services/subject_service.py
Add, view, and delete courses.
"""
from rich.table import Table
from models.classes import Subject
from services.base_service import BaseService
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_text,
    prompt_name,
    prompt_course_code,
    prompt_positive_int,
    show_spinner
)


class SubjectService(BaseService):
    section_title = "📚 Manage Subjects"
    section_subtitle = "View, add, or delete your courses"
    menu_options = [
        ("📋 View All Subjects", "view_all"),
        ("➕ Add New Subject", "add"),
        ("🗑️  Delete Subject", "delete"),
    ]

    def view_all(self):
        print_header("📋 All Subjects", "List of registered courses")
        show_spinner("Loading subjects...")
        subjects = self.data["subjects"]

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
            table.add_row(s.subject_id, f"[bold]{s.code}[/bold]", s.name, s.instructor, str(s.credit_hours))

        console.print()
        console.print(table)

    def add(self):
        print_header("➕ Add New Subject", "Register a new course")

        name = prompt_text("📖 Subject Name:")
        code = prompt_course_code("🔖 Course Code (e.g., SWE301):")

        # Make sure the course code is not already used
        if any(s.code == code for s in self.data["subjects"]):
            print_error(f"Subject with code '{code}' already exists.")
            return

        instructor = prompt_name("👨‍🏫 Instructor Name:")
        credit_hours = prompt_positive_int("⏱️  Credit Hours:", default_value=3)

        new_subject = Subject(self.next_id("subjects", "SUB", "subject_id"), name, code, instructor, credit_hours)

        show_spinner("Saving subject...")
        self.data["subjects"].append(new_subject)
        self.save()
        print_success(f"Subject '{name}' ({code}) added successfully.")

    def can_delete(self, target):
        # Prevent deleting a subject if it still has tasks, projects, or exams
        sid = target.subject_id
        linked = (
            any(t.subject_id == sid for t in self.data.get("tasks", []))
            or any(p.subject_id == sid for p in self.data.get("projects", []))
            or any(e.subject_id == sid for e in self.data.get("exams", []))
        )
        if linked:
            print_error("Cannot delete this subject because it has linked tasks, projects, or exams.")
            return False
        return True

    def delete(self):
        print_header("🗑️  Delete Subject", "Remove an existing course")
        self.delete_record("subjects", lambda s: f"[{s.subject_id}] {s.code} - {s.name}", "subject")


def manage_subjects_menu(data):
    SubjectService(data).run()