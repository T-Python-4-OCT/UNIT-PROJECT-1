from datetime import date
from rich.table import Table
from models.classes import Exam
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_required_text,
    prompt_select,
    show_spinner
)

def manage_exams_menu(data):
    while True:
        print_header(
            "SECTION: Exam Management",
            "Schedule exams, record scores, or remove exams"
        )
        choices = [
            "1. View All Exams",
            "2. Add New Exam",
            "3. Record Exam Score",
            "4. Delete Exam",
            "5. Back to Main Menu"
        ]
        choice = prompt_select("Select an action:", choices)

        if choice is None or "5." in choice:
            break
        elif "1." in choice:
            view_all_exams(data)
        elif "2." in choice:
            add_exam(data)
        elif "3." in choice:
            record_exam_score(data)
        elif "4." in choice:
            delete_exam(data)

def view_all_exams(data):
    print_header("VIEW: All Exams", "Scheduled assessments and recorded grades")
    show_spinner("Loading exams...")
    exams = data["exams"]
    
    if not exams:
        print_info("No exams scheduled yet.")
        return

    sub_map = {s.subject_id: s.code for s in data["subjects"]}

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
        score_str = f"{e.earned_score}/{e.max_score}" if e.earned_score is not None else "Pending"
        table.add_row(e.exam_id, e.title, course_code, e.exam_type, e.exam_date, e.exam_time, score_str)

    console.print()
    console.print(table)

def generate_next_exam_id(exams):
    max_num = 0
    for e in exams:
        if e.exam_id.startswith("EXM-"):
            num_part = e.exam_id.replace("EXM-", "")
            if num_part.isdigit():
                num = int(num_part)
                if num > max_num:
                    max_num = num
    return f"EXM-{max_num + 1:03d}"

def add_exam(data):
    print_header("ACTION: Add New Exam", "Schedule a new test or exam")
    if not data["subjects"]:
        print_error("Please add a subject first.")
        return

    sub_choices = [f"[{s.subject_id}] {s.code} - {s.name}" for s in data["subjects"]]
    selected_sub = prompt_select("Select Course:", sub_choices)
    if not selected_sub:
        return

    sub_id = selected_sub.split("]")[0].replace("[", "").strip()
    title = prompt_required_text("Enter Exam Title:")
    exam_type = prompt_select("Select Exam Type:", ["Midterm", "Final", "Quiz", "Practical"]) or "Midterm"
    exam_date = prompt_required_text("Enter Exam Date (YYYY-MM-DD):", default_value=str(date.today()))
    exam_time = prompt_required_text("Enter Exam Time (HH:MM):", default_value="09:00")

    new_id = generate_next_exam_id(data["exams"])
    new_exam = Exam(new_id, title, sub_id, exam_date, exam_time, exam_type)

    show_spinner("Saving exam...")
    data["exams"].append(new_exam)
    save_data(data)
    print_success(f"Exam '{title}' scheduled successfully.")

def record_exam_score(data):
    print_header("ACTION: Record Exam Score", "Enter or update grade for an exam")
    if not data["exams"]:
        print_info("No exams available.")
        return

    choices = [f"[{e.exam_id}] {e.title}" for e in data["exams"]]
    choices.append("Cancel")

    selected = prompt_select("Select exam:", choices)
    if not selected or selected == "Cancel":
        return

    exam_id = selected.split("]")[0].replace("[", "").strip()
    target_exam = next((e for e in data["exams"] if e.exam_id == exam_id), None)
    if not target_exam:
        return

    earned = prompt_required_text("Enter Earned Score:", default_value="90")
    max_s = prompt_required_text("Enter Maximum Score:", default_value="100")

    target_exam.set_earned_score(earned)
    target_exam.set_max_score(max_s)

    show_spinner("Updating exam score...")
    save_data(data)
    print_success("Exam score updated successfully.")

def delete_exam(data):
    print_header("ACTION: Delete Exam", "Remove an exam from schedule")
    if not data["exams"]:
        print_info("No exams available.")
        return

    choices = [f"[{e.exam_id}] {e.title}" for e in data["exams"]]
    choices.append("Cancel")

    selected = prompt_select("Select exam to delete:", choices)
    if not selected or selected == "Cancel":
        return

    exam_id = selected.split("]")[0].replace("[", "").strip()
    data["exams"] = [e for e in data["exams"] if e.exam_id != exam_id]
    save_data(data)
    print_success("Exam deleted successfully.")