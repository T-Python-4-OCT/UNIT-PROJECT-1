"""Service module for academic progress reports and grade analysis."""

from rich.table import Table
from rich.panel import Panel
from utils import (
    console,
    print_header,
    print_info,
    get_subject_label,
    format_grade_text,
    create_rich_progress_bar,
    show_spinner
)


def view_academic_progress(data):
    """Display comprehensive academic dashboard with clear titles for every section."""
    show_spinner("Generating Academic Progress & Grades Report...")
    print_header(
        "REPORT: Academic Progress & Grades Dashboard",
        "Complete summary of your course grades, task completion rates, and urgent alerts"
    )

    total_subjects = len(data["subjects"])
    total_tasks = len(data["tasks"])

    completed_tasks = 0
    overdue_tasks = 0
    for t in data["tasks"]:
        if t.status == "Completed":
            completed_tasks += 1
        if t.is_overdue():
            overdue_tasks += 1

    upcoming_exams_count = 0
    for e in data["exams"]:
        if e.is_upcoming():
            upcoming_exams_count += 1

    all_percentages = []
    for t in data["tasks"]:
        if t.earned_score is not None and t.max_score and t.max_score > 0:
            all_percentages.append((t.earned_score / t.max_score) * 100.0)

    for e in data["exams"]:
        if e.earned_score is not None and e.max_score and e.max_score > 0:
            all_percentages.append((e.earned_score / e.max_score) * 100.0)

    if len(all_percentages) > 0:
        overall_avg = sum(all_percentages) / len(all_percentages)
        _, overall_grade_text = format_grade_text(overall_avg)
    else:
        overall_grade_text = "No Grades Recorded Yet"

    # 1. General Summary Panel
    overdue_display = f"[bold red]{overdue_tasks} Overdue (Needs Action)[/bold red]" if overdue_tasks > 0 else "0 (None)"
    summary_text = (
        f"Registered Subjects       : {total_subjects}\n"
        f"Tasks Completed           : {completed_tasks} out of {total_tasks}\n"
        f"Overdue Tasks             : {overdue_display}\n"
        f"Upcoming Scheduled Exams  : {upcoming_exams_count}\n"
        f"Overall Grade Standing    : {overall_grade_text}"
    )
    console.print()
    console.print(Panel(summary_text, title="1. General Academic Overview", border_style="cyan", expand=False))

    # 2. Subject-by-Subject Grade Breakdown Table
    if len(data["subjects"]) > 0:
        subject_table = Table(
            title="2. Subject Grade Analysis & Task Completion Table",
            show_header=True,
            header_style="bold cyan"
        )
        subject_table.add_column("Course Code", width=13)
        subject_table.add_column("Subject Name", width=26)
        subject_table.add_column("Tasks Done", justify="center", width=12)
        subject_table.add_column("Completion Bar", justify="center", width=20)
        subject_table.add_column("Graded Items", justify="center", width=14)
        subject_table.add_column("Subject Grade & Standing", width=32)

        for sub in data["subjects"]:
            sub_tasks = []
            sub_done = 0
            for t in data["tasks"]:
                if t.subject_id == sub.subject_id:
                    sub_tasks.append(t)
                    if t.status == "Completed":
                        sub_done += 1

            sub_scores = []
            for t in sub_tasks:
                if t.earned_score is not None and t.max_score and t.max_score > 0:
                    sub_scores.append((t.earned_score / t.max_score) * 100.0)

            for e in data["exams"]:
                if e.subject_id == sub.subject_id and e.earned_score is not None and e.max_score > 0:
                    sub_scores.append((e.earned_score / e.max_score) * 100.0)

            if len(sub_scores) > 0:
                sub_avg = sum(sub_scores) / len(sub_scores)
                _, grade_str = format_grade_text(sub_avg)
            else:
                grade_str = "No Grades Recorded"

            subject_table.add_row(
                sub.code,
                sub.name,
                f"{sub_done}/{len(sub_tasks)}",
                create_rich_progress_bar(sub_done, len(sub_tasks), width=16),
                str(len(sub_scores)),
                grade_str
            )

        console.print()
        console.print(subject_table)

    # 3. Urgent Deadlines Alert Table (Overdue or Due within 7 days)
    urgent_tasks = []
    for t in data["tasks"]:
        if t.status != "Completed" and (t.is_overdue() or t.days_until_due() <= 7):
            urgent_tasks.append(t)

    if len(urgent_tasks) > 0:
        alert_table = Table(
            title="3. Urgent Tasks Alert (Overdue or Due Within 7 Days)",
            show_header=True,
            header_style="bold cyan"
        )
        alert_table.add_column("ID", width=10)
        alert_table.add_column("Task Title", width=26)
        alert_table.add_column("Subject", width=26)
        alert_table.add_column("Due Date", justify="center", width=14)
        alert_table.add_column("Urgency Status", width=28)

        for t in urgent_tasks:
            if t.is_overdue():
                status_str = f"[bold red]OVERDUE ({abs(t.days_until_due())}d late)[/bold red]"
            elif t.days_until_due() == 0:
                status_str = "[bold red]DUE TODAY[/bold red]"
            else:
                status_str = f"[yellow]Due in {t.days_until_due()} days[/yellow]"

            alert_table.add_row(
                t.task_id,
                t.title,
                get_subject_label(data["subjects"], t.subject_id),
                t.due_date,
                status_str
            )

        console.print()
        console.print(alert_table)
    else:
        print_info("No overdue or urgent tasks due within the next 7 days.")