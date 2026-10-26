"""
services/exam_service.py
Schedule exams, record grades, and delete exams.
"""
from datetime import date
from rich.table import Table
from models.classes import Exam
from services.base_service import BaseService
from utils import (
    console,
    print_header,
    print_success,
    print_info,
    prompt_text,
    prompt_date,
    prompt_time,
    prompt_float_range,
    prompt_select,
    show_spinner
)


class ExamService(BaseService):
    section_title = "🎓 Manage Exams"
    section_subtitle = "Schedule exams, record scores, or remove exams"
    menu_options = [
        ("📋 View All Exams", "view_all"),
        ("➕ Add New Exam", "add"),
        ("⭐ Record Exam Score", "record_score"),
        ("🗑️  Delete Exam", "delete"),
    ]

    def view_all(self):
        print_header("📋 All Exams", "Scheduled exams and recorded grades")
        show_spinner("Loading exams...")
        exams = self.data["exams"]

        if not exams:
            print_info("No exams scheduled yet.")
            return

        sub_map = {s.subject_id: s.code for s in self.data["subjects"]}

        table = Table(title=f"Scheduled Exams (Total: {len(exams)})", show_header=True, header_style="bold cyan")
        table.add_column("Exam ID", width=10)
        table.add_column("Title", width=25)
        table.add_column("Course", width=10)
        table.add_column("Type", width=12)
        table.add_column("Date", width=12)
        table.add_column("Time", width=8)
        table.add_column("Score", width=12)

        for e in exams:
            course_code = sub_map.get(e.subject_id, "N/A")
            score_str = f"{e.earned_score:g}/{e.max_score:g}" if e.earned_score is not None else "⏳ Pending"
            table.add_row(e.exam_id, e.title, course_code, e.exam_type, e.exam_date, e.exam_time, score_str)

        console.print()
        console.print(table)

    def add(self):
        print_header("➕ Add New Exam", "Schedule a new test or exam")

        subject = self.select_subject()
        if not subject:
            return

        title = prompt_text("📝 Exam Title:")
        exam_type = prompt_select("📌 Exam Type:", ["Midterm", "Final", "Quiz", "Practical"]) or "Midterm"
        exam_date = prompt_date("📅 Exam Date (YYYY-MM-DD):", default_value=str(date.today()))
        exam_time = prompt_time("🕘 Exam Time (HH:MM):", default_value="09:00")

        new_exam = Exam(self.next_id("exams", "EXM", "exam_id"), title, subject.subject_id,
                        exam_date, exam_time, exam_type)

        show_spinner("Saving exam...")
        self.data["exams"].append(new_exam)
        self.save()
        print_success(f"Exam '{title}' scheduled successfully.")

    def record_score(self):
        print_header("⭐ Record Exam Score", "Enter or update grade for an exam")
        if not self.data["exams"]:
            print_info("No exams available.")
            return

        exam = self.select_item(self.data["exams"], lambda e: f"[{e.exam_id}] {e.title}", "Select exam:")
        if not exam:
            return

        max_s = prompt_float_range("🎯 Maximum Score:", 0, None, default_value=100, min_exclusive=True)
        earned = prompt_float_range(f"⭐ Earned Score (0 - {max_s:g}):", 0, max_s,
                                    default_value=min(90, max_s))

        exam.set_earned_score(earned)
        exam.set_max_score(max_s)

        show_spinner("Updating exam score...")
        self.save()
        print_success("Exam score updated successfully.")

    def delete(self):
        print_header("🗑️  Delete Exam", "Remove an exam from schedule")
        self.delete_record("exams", lambda e: f"[{e.exam_id}] {e.title}", "exam")


def manage_exams_menu(data):
    ExamService(data).run()