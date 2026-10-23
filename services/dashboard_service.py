from rich.table import Table
from rich.panel import Panel
from utils import console, print_header, print_info, prompt_select, show_spinner

def format_colored_score(score):
    """Return colored percentage string based on academic performance."""
    if score >= 85:
        return f"[bold green]{score:.1f}% (High)[/bold green]"
    elif score >= 70:
        return f"[bold cyan]{score:.1f}% (Good)[/bold cyan]"
    elif score >= 60:
        return f"[bold yellow]{score:.1f}% (Moderate)[/bold yellow]"
    else:
        return f"[bold red]{score:.1f}% (Low)[/bold red]"

def get_course_status_and_color(avg):
    """Return formatted course average and multi-scenario status."""
    if avg >= 90:
        return f"[bold green]{avg:.1f}%[/bold green]", "[bold green]★ Excellent (A)[/bold green]"
    elif avg >= 80:
        return f"[cyan]{avg:.1f}%[/cyan]", "[cyan]✔ Very Good (B)[/cyan]"
    elif avg >= 70:
        return f"[blue]{avg:.1f}%[/blue]", "[blue]● Good Standing (C)[/blue]"
    elif avg >= 60:
        return f"[yellow]{avg:.1f}%[/yellow]", "[bold yellow]⚠ Needs Attention (D)[/bold yellow]"
    else:
        return f"[bold red]{avg:.1f}%[/bold red]", "[bold red]✖ At Risk (F)[/bold red]"

def show_dashboard(data):
    print_header("Dashboard: Academic Progress & Grades", "Overview of your performance, tasks, projects, and exams")
    show_spinner("Calculating your academic stats...")

    subjects = data.get("subjects", [])
    tasks = data.get("tasks", [])
    projects = data.get("projects", [])
    exams = data.get("exams", [])

    if not subjects:
        print_info("No subjects found. Please add subjects first.")
        return

    total_subjects = len(subjects)
    total_hours = sum(s.credit_hours for s in subjects)
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "Completed")
    task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    total_projects = len(projects)
    avg_project_progress = (sum(p.progress for p in projects) / total_projects) if total_projects > 0 else 0.0

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

    # Color-coded progress indicators for top summary panel
    task_prog_color = "green" if task_completion_rate >= 75 else ("yellow" if task_completion_rate >= 40 else "red")
    proj_prog_color = "green" if avg_project_progress >= 75 else ("yellow" if avg_project_progress >= 40 else "red")

    summary_text = (
        f"[bold white]Total Courses:[/bold white]         [cyan]{total_subjects} Courses ({total_hours} Credit Hours)[/cyan]\n"
        f"[bold white]Tasks Completion:[/bold white]      [{task_prog_color}]{completed_tasks}/{total_tasks} completed ({task_completion_rate:.1f}%)[/{task_prog_color}]\n"
        f"[bold white]Projects Progress:[/bold white]     [{proj_prog_color}]{avg_project_progress:.1f}% across {total_projects} projects[/{proj_prog_color}]\n"
        f"[bold white]Average Task Score:[/bold white]    {format_colored_score(avg_task_score)}\n"
        f"[bold white]Average Exam Score:[/bold white]    {format_colored_score(avg_exam_score)}"
    )
    console.print(Panel(summary_text, title="[bold cyan]Overall Performance Summary[/bold cyan]", border_style="cyan"))

    table = Table(title="Course Performance Breakdown", show_header=True, header_style="bold cyan")
    table.add_column("Code", width=10)
    table.add_column("Course Name", width=28)
    table.add_column("Hours", width=7)
    table.add_column("Tasks Done", width=12)
    table.add_column("Project %", width=12)
    table.add_column("Course Avg", width=12)
    table.add_column("Academic Status", width=22)

    for sub in subjects:
        sub_tasks = [t for t in tasks if t.subject_id == sub.subject_id]
        sub_done = sum(1 for t in sub_tasks if t.status == "Completed")
        
        if len(sub_tasks) > 0:
            t_ratio = sub_done / len(sub_tasks)
            t_color = "green" if t_ratio == 1 else ("yellow" if t_ratio >= 0.5 else "red")
            tasks_str = f"[{t_color}]{sub_done}/{len(sub_tasks)}[/{t_color}]"
        else:
            tasks_str = "[dim]0/0[/dim]"

        sub_projects = [p for p in projects if p.subject_id == sub.subject_id]
        if sub_projects:
            p_val = sum(p.progress for p in sub_projects) // len(sub_projects)
            p_color = "green" if p_val >= 80 else ("cyan" if p_val >= 50 else "yellow")
            proj_str = f"[{p_color}]{p_val}%[/{p_color}]"
        else:
            proj_str = "[dim]N/A[/dim]"

        sub_exams = [e for e in exams if e.subject_id == sub.subject_id]
        
        scores = []
        for t in sub_tasks:
            if t.earned_score is not None and t.max_score:
                scores.append((t.earned_score / t.max_score) * 100)
        for p in sub_projects:
            if p.earned_score is not None and p.max_score:
                scores.append((p.earned_score / p.max_score) * 100)
        for e in sub_exams:
            if e.earned_score is not None and e.max_score:
                scores.append((e.earned_score / e.max_score) * 100)

        if scores:
            avg = sum(scores) / len(scores)
            avg_str, status = get_course_status_and_color(avg)
        else:
            avg_str = "[dim]N/A[/dim]"
            status = "[dim]⏳ Pending Grades[/dim]"

        table.add_row(
            f"[bold]{sub.code}[/bold]",
            sub.name,
            str(sub.credit_hours),
            tasks_str,
            proj_str,
            avg_str,
            status
        )

    console.print()
    console.print(table)
    prompt_select("Return to menu:", ["Back to Main Menu"])