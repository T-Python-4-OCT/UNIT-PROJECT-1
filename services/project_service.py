from datetime import date, timedelta
from rich.table import Table
from rich.panel import Panel
from models.classes import Project
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
    prompt_checkbox,
    confirm_delete,
    show_spinner
)

def manage_projects_menu(data):
    while True:
        print_header(
            "SECTION: Academic Projects Tracker",
            "Complete project steps or add progress % to finish your term projects"
        )
        choices = [
            "1. View All Projects",
            "2. Add New Project",
            "3. Complete Project Step / Add Progress %",
            "4. Delete Project",
            "5. Back to Main Menu"
        ]
        choice = prompt_select("Select an action:", choices)

        if choice is None or "5." in choice:
            break
        elif "1." in choice:
            view_all_projects(data)
        elif "2." in choice:
            add_project(data)
        elif "3." in choice:
            update_project_progress(data)
        elif "4." in choice:
            delete_project(data)

def render_progress_bar(percentage):
    filled = int(percentage // 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    color = "green" if percentage == 100 else ("cyan" if percentage >= 60 else "yellow")
    return f"[{color}]{bar} {percentage}%[/{color}]"

def format_project_score(earned, max_s):
    if earned is None or max_s is None or max_s <= 0:
        return "[dim]Pending[/dim]"
    pct = (earned / max_s) * 100
    color = "bold green" if pct >= 85 else ("cyan" if pct >= 70 else ("yellow" if pct >= 60 else "bold red"))
    return f"[{color}]{earned:g}/{max_s:g} ({pct:.0f}%)[/{color}]"

def celebrate_project_completion(project):
    """Display a clear green celebration panel when a project hits 100%."""
    console.print()
    console.print(
        Panel(
            f"[bold green]🎉 CONGRATULATIONS! PROJECT COMPLETED (100%)![/bold green]\n"
            f"[bold white]Project:[/bold white] {project.title}\n"
            f"[bold white]Status:[/bold white]  [bold green]✔ All Milestones Accomplished ({ render_progress_bar(100) })[/bold green]",
            title="[bold green]★ Project Accomplished ★[/bold green]",
            border_style="green"
        )
    )
    earned = prompt_required_text("Enter Final Project Earned Score:", default_value="95")
    max_s = prompt_required_text("Enter Maximum Score:", default_value="100")
    project.set_earned_score(earned)
    project.set_max_score(max_s)

def view_all_projects(data):
    print_header("VIEW: All Academic Projects", "Track your milestones, remaining percentage, and final grades")
    show_spinner("Loading projects...")
    projects = data.get("projects", [])

    if not projects:
        print_info("No projects available.")
        return

    sub_map = {s.subject_id: s.code for s in data["subjects"]}

    table = Table(title=f"Academic Projects (Total: {len(projects)})", show_header=True, header_style="bold cyan")
    table.add_column("ID", width=9)
    table.add_column("Project Title", width=28)
    table.add_column("Course", width=9)
    table.add_column("Current Status / Phase", width=24)
    table.add_column("Steps", width=8)
    table.add_column("Progress", width=18)
    table.add_column("Deadline", width=12)
    table.add_column("Score", width=16)

    for p in projects:
        course_code = sub_map.get(p.subject_id, "N/A")
        score_str = format_project_score(p.earned_score, p.max_score)
        phase_str = "✔ Completed" if p.progress == 100 else p.phase
        phase_color = "bold green" if p.progress == 100 else "magenta"
        steps_str = f"{len(p.completed_steps)}/{len(Project.MILESTONES)}"

        table.add_row(
            p.project_id,
            p.title,
            f"[bold]{course_code}[/bold]",
            f"[{phase_color}]{phase_str}[/{phase_color}]",
            steps_str,
            render_progress_bar(p.progress),
            p.deadline,
            score_str
        )

    console.print()
    console.print(table)

def generate_next_project_id(projects):
    max_num = 0
    for p in projects:
        if p.project_id.startswith("PRJ-"):
            num_part = p.project_id.replace("PRJ-", "")
            if num_part.isdigit():
                num = int(num_part)
                if num > max_num:
                    max_num = num
    return f"PRJ-{max_num + 1:03d}"

def add_project(data):
    print_header("ACTION: Add New Project", "Create a new course project with milestone tracking")
    if not data["subjects"]:
        print_error("Please add a subject first.")
        return

    sub_choices = [f"[{s.subject_id}] {s.code} - {s.name}" for s in data["subjects"]]
    selected_sub = prompt_select("Select Course:", sub_choices)
    if not selected_sub:
        return

    sub_id = selected_sub.split("]")[0].replace("[", "").strip()

    title = prompt_required_text("Enter Project Title:")
    deadline = prompt_required_text("Enter Deadline (YYYY-MM-DD):", default_value=str(date.today() + timedelta(days=30)))
    completed_steps = prompt_checkbox(
        "Select any milestones already completed (Press Space to check, Enter to confirm):",
        Project.MILESTONES
    ) or []

    new_id = generate_next_project_id(data["projects"])
    new_project = Project(new_id, title, sub_id, deadline, completed_steps=completed_steps)

    if new_project.progress == 100:
        celebrate_project_completion(new_project)

    show_spinner("Saving project...")
    data["projects"].append(new_project)
    save_data(data)
    print_success(f"Project '{title}' added! Current progress: {new_project.progress}%.")

def update_project_progress(data):
    print_header("ACTION: Update Project Progress", "Complete remaining steps or add percentage to finish your project")
    if not data.get("projects"):
        print_info("No projects available.")
        return

    choices = [
        f"[{p.project_id}] {p.title} (Current: {p.progress}% - {100 - p.progress}% remaining)"
        for p in data["projects"]
    ]
    choices.append("Cancel")

    selected = prompt_select("Select project to update:", choices)
    if not selected or selected == "Cancel":
        return

    prj_id = selected.split("]")[0].replace("[", "").strip()
    target = next((p for p in data["projects"] if p.project_id == prj_id), None)
    if not target:
        return

    old_progress = target.progress
    remaining_pct = 100 - old_progress

    console.print(
        Panel(
            f"[bold cyan]Project:[/bold cyan] {target.title}\n"
            f"[bold cyan]Current Progress:[/bold cyan] {render_progress_bar(old_progress)} "
            f"([yellow]{remaining_pct}% remaining to complete[/yellow])\n"
            f"[bold cyan]Current Phase:[/bold cyan] {target.phase}",
            border_style="cyan"
        )
    )

    remaining_steps = [m for m in Project.MILESTONES if m not in target.completed_steps]
    action_choices = []

    if remaining_steps:
        next_step = remaining_steps[0]
        action_choices.append(f"1. Complete Next Milestone: '{next_step}' (+20%)")
    if remaining_pct > 0:
        action_choices.append(f"2. Complete Remaining {remaining_pct}% Now (Finish Project -> 100%)")
        action_choices.append("3. Add Custom Progress Percentage (e.g., +10%)")
    action_choices.append("4. Choose Multiple Milestones (Checklist)")
    action_choices.append("5. Cancel")

    action = prompt_select("How would you like to update your progress?", action_choices)
    if not action or "Cancel" in action:
        return

    if "Complete Next Milestone:" in action:
        target.complete_single_milestone(remaining_steps[0])
        if target.progress < old_progress + 20:
            target.add_progress_amount(20)
    elif f"Complete Remaining {remaining_pct}% Now" in action:
        target.set_progress(100)
    elif "Add Custom Progress Percentage" in action:
        add_val = prompt_positive_int(f"Enter percentage to add (1 to {remaining_pct}):", default_value=str(min(10, remaining_pct)))
        target.add_progress_amount(add_val)
    elif "Choose Multiple Milestones" in action:
        selected_steps = prompt_checkbox(
            "Use SPACE to check/uncheck milestones, then press ENTER:",
            Project.MILESTONES,
            checked_items=target.completed_steps
        )
        if selected_steps is None:
            return
        target.update_milestones(selected_steps)

    if target.progress == 100:
        celebrate_project_completion(target)
    else:
        target.set_earned_score(None)
        console.print(
            Panel(
                f"[bold green]✔ Progress Updated:[/bold green] {old_progress}% ➔ [bold cyan]{target.progress}%[/bold cyan]\n"
                f"[bold white]Remaining to finish:[/bold white] [yellow]{100 - target.progress}%[/yellow] | "
                f"[bold white]Next Phase:[/bold white] [magenta]{target.phase}[/magenta]",
                border_style="green"
            )
        )

    show_spinner("Saving project progress...")
    save_data(data)
    print_success(f"Project '{target.title}' saved at {target.progress}%.")

def delete_project(data):
    print_header("ACTION: Delete Project", "Remove a project")
    if not data.get("projects"):
        print_info("No projects available.")
        return

    choices = [f"[{p.project_id}] {p.title}" for p in data["projects"]]
    choices.append("Cancel")

    selected = prompt_select("Select project to delete:", choices)
    if not selected or selected == "Cancel":
        return

    prj_id = selected.split("]")[0].replace("[", "").strip()
    if confirm_delete(selected):
        data["projects"] = [p for p in data["projects"] if p.project_id != prj_id]
        save_data(data)
        print_success("Project deleted successfully.")
    else:
        print_info("Deletion cancelled.")