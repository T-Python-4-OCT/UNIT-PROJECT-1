"""
services/dashboard_service.py
Displays overall academic summary and course grades table.
"""
from rich.table import Table
from rich.panel import Panel
from utils import console, print_header, print_info, prompt_select, show_spinner


def format_colored_score(score):
    if score >= 85:
        return f"[bold green]{score:.1f}% (High)[/bold green]"
    elif score >= 70:
        return f"[bold cyan]{score:.1f}% (Good)[/bold cyan]"
    elif score >= 60:
        return f"[bold yellow]{score:.1f}% (Moderate)[/bold yellow]"
    else:
        return f"[bold red]{score:.1f}% (Low)[/bold red]"


def get_course_status_and_color(avg):
    if avg >= 90:
        return f"[bold green]{avg:.1f}%[/bold green]", "[bold green]🌟 Excellent (A)[/bold green]"
    elif avg >= 80:
        return f"[cyan]{avg:.1f}%[/cyan]", "[cyan]✅ Very Good (B)[/cyan]"
    elif avg >= 70:
        return f"[blue]{avg:.1f}%[/blue]", "[blue]🔵 Good Standing (C)[/blue]"
    elif avg >= 60:
        return f"[yellow]{avg:.1f}%[/yellow]", "[bold yellow]⚠️  Needs Attention (D)[/bold yellow]"
    else:
        return f"[bold red]{avg:.1f}%[/bold red]", "[bold red]🚨 At Risk (F)[/bold red]"


def percentages(items):
    return [pct for pct in (item.get_percentage() for item in items) if pct is not None]


def average(values):
    return sum(values) / len(values) if values else 0.0


def show_dashboard(data):
    print_header("📊 Academic Progress & Grades", "Overview of your courses, tasks, projects, and exams")
    show_spinner("Calculating your academic stats...")

    subjects = data.get("subjects", [])
    tasks = data.get("tasks", [])
    projects = data.get("projects", [])
    exams = data.get("exams", [])

    if not subjects:
        print_info("No subjects found. Please add subjects first.")
        return

    # Calculate general stats
    total_subjects = len(subjects)
    total_hours = sum(s.credit_hours for s in subjects)

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "Completed")
    task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    total_projects = len(projects)
    avg_project_progress = average([p.progress for p in projects])

    avg_task_score = average(percentages(tasks))
    avg_exam_score = average(percentages(exams))

    task_prog_color = "green" if task_completion_rate >= 75 else ("yellow" if task_completion_rate >= 40 else "red")
    proj_prog_color = "green" if avg_project_progress >= 75 else ("yellow" if avg_project_progress >= 40 else "red")

    summary_text = (
        f"[bold white]📚 Total Courses:[/bold white]         [cyan]{total_subjects} Courses ({total_hours} Credit Hours)[/cyan]\n"
        f"[bold white]📝 Tasks Completion:[/bold white]      [{task_prog_color}]{completed_tasks}/{total_tasks} completed ({task_completion_rate:.1f}%)[/{task_prog_color}]\n"
        f"[bold white]🚀 Projects Progress:[/bold white]     [{proj_prog_color}]{avg_project_progress:.1f}% across {total_projects} projects[/{proj_prog_color}]\n"
        f"[bold white]⭐ Average Task Score:[/bold white]    {format_colored_score(avg_task_score)}\n"
        f"[bold white]🎓 Average Exam Score:[/bold white]    {format_colored_score(avg_exam_score)}"
    )
    console.print(Panel(summary_text, title="[bold cyan]📈 Overall Performance Summary[/bold cyan]", border_style="cyan"))

    # Build course breakdown table
    table = Table(title="Course Performance Breakdown", show_header=True, header_style="bold cyan")
    table.add_column("Code", width=10)
    table.add_column("Course Name", width=28)
    table.add_column("Hours", width=7)
    table.add_column("Tasks Done", width=12)
    table.add_column("Project %", width=12)
    table.add_column("Course Avg", width=12)
    table.add_column("Academic Status", width=24)

    for sub in subjects:
        sub_tasks = [t for t in tasks if t.subject_id == sub.subject_id]
        sub_projects = [p for p in projects if p.subject_id == sub.subject_id]
        sub_exams = [e for e in exams if e.subject_id == sub.subject_id]

        sub_done = sum(1 for t in sub_tasks if t.status == "Completed")
        if sub_tasks:
            t_ratio = sub_done / len(sub_tasks)
            t_color = "green" if t_ratio == 1 else ("yellow" if t_ratio >= 0.5 else "red")
            tasks_str = f"[{t_color}]{sub_done}/{len(sub_tasks)}[/{t_color}]"
        else:
            tasks_str = "[dim]0/0[/dim]"

        if sub_projects:
            p_val = sum(p.progress for p in sub_projects) // len(sub_projects)
            p_color = "green" if p_val >= 80 else ("cyan" if p_val >= 50 else "yellow")
            proj_str = f"[{p_color}]{p_val}%[/{p_color}]"
        else:
            proj_str = "[dim]N/A[/dim]"

        scores = percentages(sub_tasks + sub_projects + sub_exams)
        if scores:
            avg_str, status = get_course_status_and_color(average(scores))
        else:
            avg_str = "[dim]N/A[/dim]"
            status = "[dim]⏳ Pending Grades[/dim]"

        table.add_row(f"[bold]{sub.code}[/bold]", sub.name, str(sub.credit_hours),
                      tasks_str, proj_str, avg_str, status)

    console.print()
    console.print(table)
    prompt_select("Return to menu:", ["🔙 Back to Main Menu"])