from rich.table import Table
from rich.panel import Panel
from utils import console, print_header, print_info, prompt_select, show_spinner

def show_dashboard(data):
    print_header("Dashboard: Academic Progress & Grades", "Overview of your performance, tasks, and exams")
    show_spinner("Calculating your academic stats...")

    subjects = data["subjects"]
    tasks = data["tasks"]
    exams = data["exams"]

    if not subjects:
        print_info("No subjects found. Please add subjects first.")
        return

    # 1. Calculate overall statistics
    total_subjects = len(subjects)
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if (t.status if hasattr(t, "status") else t.get("status")) == "Completed")
    task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    # Calculate average scores for tasks
    task_scores = []
    for t in tasks:
        earned = t.earned_score if hasattr(t, "earned_score") else t.get("earned_score")
        max_s = t.max_score if hasattr(t, "max_score") else t.get("max_score", 100.0)
        if earned is not None and max_s and max_s > 0:
            task_scores.append((earned / max_s) * 100)

    avg_task_score = (sum(task_scores) / len(task_scores)) if task_scores else 0.0

    # Calculate average scores for exams
    exam_scores = []
    for e in exams:
        earned = e.earned_score if hasattr(e, "earned_score") else e.get("earned_score")
        max_s = e.max_score if hasattr(e, "max_score") else e.get("max_s", 100.0)
        if earned is not None and max_s and max_s > 0:
            exam_scores.append((earned / max_s) * 100)

    avg_exam_score = (sum(exam_scores) / len(exam_scores)) if exam_scores else 0.0

    # Display Summary Panel
    summary_text = (
        f"[bold cyan]Total Courses:[/bold cyan] {total_subjects}\n"
        f"[bold cyan]Tasks Progress:[/bold cyan] {completed_tasks}/{total_tasks} completed ({task_completion_rate:.1f}%)\n"
        f"[bold cyan]Avg Task Score:[/bold cyan] {avg_task_score:.1f}%\n"
        f"[bold cyan]Avg Exam Score:[/bold cyan] {avg_exam_score:.1f}%"
    )
    console.print(Panel(summary_text, title="Performance Summary", border_style="cyan"))

    # 2. Subject Breakdown Table
    table = Table(title="Course Breakdown & Grades", show_header=True, header_style="bold cyan")
    table.add_column("Course Code", width=15)
    table.add_column("Course Name", width=25)
    table.add_column("Credit Hours", width=15)
    table.add_column("Instructor", width=20)

    for sub in subjects:
        table.add_row(
            sub.code,
            sub.name,
            str(sub.credit_hours),
            sub.instructor
        )

    console.print()
    console.print(table)
    
    prompt_select("Press Enter/Choose to return to Main Menu:", ["Back to Main Menu"])