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

    total_subjects = len(subjects)
    total_hours = sum(s.credit_hours for s in subjects)
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "Completed")
    task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    task_scores = [
        (t.earned_score / t.max_score) * 100
        for t in tasks
        if t.earned_score is not None and t.max_score and t.max_score > 0
    ]
    avg_task_score = (sum(task_scores) / len(task_scores)) if task_scores else 0.0

    exam_scores = [
        (e.earned_score / e.max_score) * 100
        for e in exams
        if e.earned_score is not None and e.max_score and e.max_score > 0
    ]
    avg_exam_score = (sum(exam_scores) / len(exam_scores)) if exam_scores else 0.0

    summary_text = (
        f"[bold cyan]Total Courses:[/bold cyan] {total_subjects} ({total_hours} Credit Hours)\n"
        f"[bold cyan]Tasks Progress:[/bold cyan] {completed_tasks}/{total_tasks} completed ({task_completion_rate:.1f}%)\n"
        f"[bold cyan]Avg Task Score:[/bold cyan] {avg_task_score:.1f}%\n"
        f"[bold cyan]Avg Exam Score:[/bold cyan] {avg_exam_score:.1f}%"
    )
    console.print(Panel(summary_text, title="Overall Performance Summary", border_style="cyan"))

    table = Table(title="Course Performance Breakdown", show_header=True, header_style="bold cyan")
    table.add_column("Code", width=10)
    table.add_column("Course Name", width=25)
    table.add_column("Hours", width=8)
    table.add_column("Tasks Done", width=12)
    table.add_column("Course Avg", width=12)
    table.add_column("Status", width=14)

    for sub in subjects:
        sub_tasks = [t for t in tasks if t.subject_id == sub.subject_id]
        sub_done = sum(1 for t in sub_tasks if t.status == "Completed")
        tasks_str = f"{sub_done}/{len(sub_tasks)}"

        sub_exams = [e for e in exams if e.subject_id == sub.subject_id]
        
        scores = []
        for t in sub_tasks:
            if t.earned_score is not None and t.max_score:
                scores.append((t.earned_score / t.max_score) * 100)
        for e in sub_exams:
            if e.earned_score is not None and e.max_score:
                scores.append((e.earned_score / e.max_score) * 100)

        if scores:
            avg = sum(scores) / len(scores)
            avg_str = f"{avg:.1f}%"
            status = "[green]Good Standing[/green]" if avg >= 60 else "[red]At Risk[/red]"
        else:
            avg_str = "N/A"
            status = "[yellow]In Progress[/yellow]"

        table.add_row(
            sub.code,
            sub.name,
            str(sub.credit_hours),
            tasks_str,
            avg_str,
            status
        )

    console.print()
    console.print(table)
    prompt_select("Return to menu:", ["Back to Main Menu"])