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
    confirm_delete,
    show_spinner
)

def manage_projects_menu(data):
    while True:
        print_header(
            "SECTION: Academic Projects Tracker",
            "Create custom project steps with weights (%) and grades, and track completion"
        )
        choices = [
            "1. View All Projects & Step Breakdown",
            "2. Add New Project (With Custom Steps, % & Grades)",
            "3. Complete / Update Project Steps",
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
    color = "bold green" if percentage == 100 else ("cyan" if percentage >= 60 else "yellow")
    return f"[{color}]{bar} {percentage}%[/{color}]"

def format_project_score(earned, max_s):
    if earned is None or max_s is None or max_s <= 0:
        return f"[dim]0/{max_s:g} (Pending)[/dim]"
    pct = (earned / max_s) * 100
    color = "bold green" if pct >= 85 else ("cyan" if pct >= 70 else ("yellow" if pct >= 60 else "bold red"))
    return f"[{color}]{earned:g}/{max_s:g} pts ({pct:.0f}%)[/{color}]"

def display_project_steps_table(project, course_code=""):
    """Display a detailed table of a project's custom steps, highlighting completed ones in green."""
    step_table = Table(
        title=f"[bold cyan]{project.project_id} — {project.title} ({course_code})[/bold cyan] | Progress: {render_progress_bar(project.progress)}",
        show_header=True,
        header_style="bold cyan"
    )
    step_table.add_column("#", width=4)
    step_table.add_column("Step Description", width=36)
    step_table.add_column("Weight (%)", width=12)
    step_table.add_column("Step Grade", width=18)
    step_table.add_column("Status", width=16)

    for idx, s in enumerate(project.steps, start=1):
        if s.get("completed"):
            name_str = f"[bold green]✔ {s['name']}[/bold green]"
            weight_str = f"[bold green]+{s['weight']}% (Done)[/bold green]"
            earned_pts = s.get("earned_points", s["max_points"])
            grade_str = f"[bold green]{earned_pts:g}/{s['max_points']:g} pts[/bold green]"
            status_str = "[bold green]✔ Completed[/bold green]"
        else:
            name_str = f"[white]{s['name']}[/white]"
            weight_str = f"[yellow]{s['weight']}%[/yellow]"
            grade_str = f"[dim]0/{s['max_points']:g} pts[/dim]"
            status_str = "[yellow]⏳ Pending[/yellow]"

        step_table.add_row(str(idx), name_str, weight_str, grade_str, status_str)

    console.print()
    console.print(step_table)

def view_all_projects(data):
    print_header("VIEW: All Academic Projects", "Overview of projects and their custom step-by-step progress")
    show_spinner("Loading projects...")
    projects = data.get("projects", [])

    if not projects:
        print_info("No projects available.")
        return

    sub_map = {s.subject_id: s.code for s in data["subjects"]}

    table = Table(title=f"Academic Projects Summary (Total: {len(projects)})", show_header=True, header_style="bold cyan")
    table.add_column("ID", width=9)
    table.add_column("Project Title", width=28)
    table.add_column("Course", width=9)
    table.add_column("Next / Current Step", width=26)
    table.add_column("Steps Done", width=12)
    table.add_column("Total Progress", width=18)
    table.add_column("Deadline", width=12)
    table.add_column("Total Score", width=18)

    for p in projects:
        course_code = sub_map.get(p.subject_id, "N/A")
        score_str = format_project_score(p.earned_score, p.max_score)
        done_count = sum(1 for s in p.steps if s.get("completed"))
        total_steps = len(p.steps)
        
        if p.progress == 100:
            phase_str = "[bold green]✔ All Steps Completed[/bold green]"
            steps_str = f"[bold green]{done_count}/{total_steps}[/bold green]"
        else:
            phase_str = f"[magenta]{p.phase}[/magenta]"
            steps_str = f"[yellow]{done_count}/{total_steps}[/yellow]"

        table.add_row(
            p.project_id,
            p.title,
            f"[bold]{course_code}[/bold]",
            phase_str,
            steps_str,
            render_progress_bar(p.progress),
            p.deadline,
            score_str
        )

    console.print()
    console.print(table)

    # Allow user to inspect any project's custom steps in detail or view all
    choices = ["View Detailed Steps for ALL Projects"] + [
        f"[{p.project_id}] {p.title} ({p.progress}%)" for p in projects
    ] + ["Back to Projects Menu"]

    selected = prompt_select("Select a project to inspect its steps (green = completed):", choices)
    if not selected or selected == "Back to Projects Menu":
        return

    if selected == "View Detailed Steps for ALL Projects":
        for p in projects:
            display_project_steps_table(p, sub_map.get(p.subject_id, "N/A"))
    else:
        prj_id = selected.split("]")[0].replace("[", "").strip()
        target = next((p for p in projects if p.project_id == prj_id), None)
        if target:
            display_project_steps_table(target, sub_map.get(target.subject_id, "N/A"))

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
    print_header("ACTION: Add New Project", "Define your project and customize its steps, weights (%), and grades")
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
    
    num_steps = prompt_positive_int("How many steps does this project have?", default_value="5")
    if num_steps <= 0:
        num_steps = 5

    console.print(
        Panel(
            f"[bold cyan]Define the {num_steps} Steps for '{title}'[/bold cyan]\n"
            f"For each step, enter its [bold white]Name[/bold white], [bold yellow]Percentage Weight (%)[/bold yellow], and [bold green]Max Grade Points[/bold green].",
            border_style="cyan"
        )
    )

    steps = []
    remaining_weight = 100
    default_points = round(100.0 / num_steps, 1)

    for i in range(1, num_steps + 1):
        console.print(f"\n[bold cyan]--- Step {i} of {num_steps} (Remaining Progress Weight: {remaining_weight}%) ---[/bold cyan]")
        step_name = prompt_required_text(f"Enter Step {i} Name:")
        
        if i == num_steps and remaining_weight > 0:
            default_w = remaining_weight
        else:
            default_w = max(5, remaining_weight // (num_steps - i + 1))

        weight = prompt_positive_int(
            f"Enter Step {i} Progress Percentage (%) [Remaining: {remaining_weight}%]:",
            default_value=str(default_w)
        )
        remaining_weight = max(0, remaining_weight - weight)

        pts_str = prompt_required_text(f"Enter Step {i} Max Grade Points:", default_value=str(default_points))
        try:
            max_pts = float(pts_str)
            if max_pts <= 0:
                max_pts = default_points
        except ValueError:
            max_pts = default_points

        is_done_choice = prompt_select(
            f"Have you already completed Step {i} ('{step_name}')?",
            ["No (Pending)", "Yes (Completed ✔)"]
        )
        is_done = is_done_choice == "Yes (Completed ✔)"
        earned_pts = None

        if is_done:
            ep_str = prompt_required_text(f"Enter Earned Points for Step {i} (out of {max_pts:g}):", default_value=str(max_pts))
            try:
                earned_pts = min(float(ep_str), max_pts)
            except ValueError:
                earned_pts = max_pts

        steps.append({
            "name": step_name,
            "weight": weight,
            "max_points": max_pts,
            "earned_points": earned_pts,
            "completed": is_done
        })

    new_id = generate_next_project_id(data["projects"])
    new_project = Project(new_id, title, sub_id, deadline, steps=steps)

    show_spinner("Saving project and calculating step progress...")
    data["projects"].append(new_project)
    save_data(data)

    sub_code = next((s.code for s in data["subjects"] if s.subject_id == sub_id), "")
    display_project_steps_table(new_project, sub_code)
    print_success(f"Project '{title}' added! Completed Progress: {new_project.progress}%.")

def update_project_progress(data):
    print_header("ACTION: Complete / Manage Project Steps", "Select a step to mark it completed (Green) and update your progress %")
    if not data.get("projects"):
        print_info("No projects available.")
        return

    sub_map = {s.subject_id: s.code for s in data["subjects"]}
    choices = [
        f"[{p.project_id}] {p.title} ({sub_map.get(p.subject_id, 'N/A')}) — Progress: {p.progress}%"
        for p in data["projects"]
    ]
    choices.append("Cancel")

    selected = prompt_select("Select a project to update its steps:", choices)
    if not selected or selected == "Cancel":
        return

    prj_id = selected.split("]")[0].replace("[", "").strip()
    target = next((p for p in data["projects"] if p.project_id == prj_id), None)
    if not target:
        return

    course_code = sub_map.get(target.subject_id, "N/A")

    while True:
        display_project_steps_table(target, course_code)

        step_choices = []
        for idx, s in enumerate(target.steps):
            if s.get("completed"):
                earned = s.get("earned_points", s["max_points"])
                step_choices.append(
                    f"Step {idx + 1}: ✔ [COMPLETED] {s['name']} (+{s['weight']}% | {earned:g}/{s['max_points']:g} pts) — Select to Undo/Edit"
                )
            else:
                step_choices.append(
                    f"Step {idx + 1}: ⏳ [PENDING]   {s['name']} (+{s['weight']}% | {s['max_points']:g} pts) — Select to Complete"
                )
        step_choices.append("Done / Back to Projects Menu")

        chosen_step = prompt_select("Choose a step to complete or update:", step_choices)
        if not chosen_step or chosen_step == "Done / Back to Projects Menu":
            break

        step_idx = int(chosen_step.split(":")[0].replace("Step ", "").strip()) - 1
        step_obj = target.steps[step_idx]

        if not step_obj.get("completed"):
            old_prog = target.progress
            earned_str = prompt_required_text(
                f"Enter Earned Grade Points for '{step_obj['name']}' (Max {step_obj['max_points']:g} pts):",
                default_value=str(step_obj['max_points'])
            )
            target.complete_step(step_idx, earned_str)
            save_data(data)

            console.print(
                Panel(
                    f"[bold green]✔ Step Completed:[/bold green] [bold white]{step_obj['name']}[/bold white]\n"
                    f"[bold green]Progress Added:[/bold green] +{step_obj['weight']}%  ({old_prog}% ➔ [bold green]{target.progress}%[/bold green])\n"
                    f"[bold green]Step Score:[/bold green]     {step_obj['earned_points']:g} / {step_obj['max_points']:g} pts\n"
                    f"[bold cyan]Overall Progress:[/bold cyan] {render_progress_bar(target.progress)}",
                    title="[bold green]Step Accomplished![/bold green]",
                    border_style="green"
                )
            )

            if target.progress == 100:
                console.print(
                    Panel(
                        f"[bold green]🎉 CONGRATULATIONS! ALL PROJECT STEPS COMPLETED (100%)![/bold green]\n"
                        f"[bold white]Project:[/bold white] {target.title}\n"
                        f"[bold white]Total Project Score:[/bold white] [bold green]{target.earned_score:g} / {target.max_score:g} pts[/bold green]",
                        title="[bold green]★ Project 100% Accomplished ★[/bold green]",
                        border_style="green"
                    )
                )
        else:
            action = prompt_select(
                f"Step '{step_obj['name']}' is already completed. What would you like to do?",
                [
                    "1. Update Earned Grade Points",
                    "2. Mark as Pending (Uncheck Step)",
                    "3. Cancel"
                ]
            )
            if action and "1." in action:
                earned_str = prompt_required_text(
                    f"Enter New Earned Points (Max {step_obj['max_points']:g} pts):",
                    default_value=str(step_obj.get("earned_points", step_obj["max_points"]))
                )
                target.complete_step(step_idx, earned_str)
                save_data(data)
                print_success("Step score updated.")
            elif action and "2." in action:
                target.uncomplete_step(step_idx)
                save_data(data)
                print_info(f"Step '{step_obj['name']}' marked as Pending. Progress is now {target.progress}%.")

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