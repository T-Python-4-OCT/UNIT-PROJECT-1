from datetime import date, timedelta
from faker import Faker
from rich.table import Table
from models.classes import Project
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_required_text,
    prompt_select,
    prompt_checkbox,
    show_spinner
)

fake = Faker()

def manage_projects_menu(data):
    while True:
        print_header(
            "SECTION: Academic Projects Tracker",
            "Complete project milestones to automatically increase your progress %"
        )
        choices = [
            "1. View All Projects",
            "2. Add New Project (Manual or Auto-Faker)",
            "3. Check/Uncheck Project Milestones (Auto-Update %)",
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

def view_all_projects(data):
    print_header("VIEW: All Academic Projects", "Each completed milestone automatically adds 20% to progress")
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
    table.add_column("Current/Next Milestone", width=24)
    table.add_column("Steps Done", width=12)
    table.add_column("Auto Progress", width=18)
    table.add_column("Deadline", width=12)
    table.add_column("Score", width=10)

    for p in projects:
        course_code = sub_map.get(p.subject_id, "N/A")
        score_str = f"{p.earned_score}/{p.max_score}" if p.earned_score is not None else "-"
        phase_color = "green" if p.phase == "Completed" else "magenta"
        steps_str = f"{len(p.completed_steps)}/{len(Project.MILESTONES)}"

        table.add_row(
            p.project_id,
            p.title,
            course_code,
            f"[{phase_color}]{p.phase}[/{phase_color}]",
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

    mode = prompt_select(
        "How would you like to add the project?",
        ["1. Auto-generate with Faker", "2. Enter manually"]
    )
    if not mode:
        return

    if "1." in mode:
        title = fake.catch_phrase().title()
        deadline = (date.today() + timedelta(days=fake.random_int(min=7, max=45))).strftime("%Y-%m-%d")
        num_done = fake.random_int(min=1, max=4)
        completed_steps = Project.MILESTONES[:num_done]
    else:
        title = prompt_required_text("Enter Project Title:", default_value=fake.catch_phrase().title())
        deadline = prompt_required_text("Enter Deadline (YYYY-MM-DD):", default_value=str(date.today() + timedelta(days=30)))
        completed_steps = prompt_checkbox(
            "Select any milestones already completed (Press Space to check, Enter to confirm):",
            Project.MILESTONES
        ) or []

    new_id = generate_next_project_id(data["projects"])
    new_project = Project(new_id, title, sub_id, deadline, completed_steps=completed_steps)

    show_spinner("Saving project...")
    data["projects"].append(new_project)
    save_data(data)
    print_success(f"Project '{title}' added! Auto-calculated progress: {new_project.progress}%.")

def update_project_progress(data):
    print_header("ACTION: Check Project Milestones", "Each checked step adds 20% to your project progress")
    if not data.get("projects"):
        print_info("No projects available.")
        return

    choices = [f"[{p.project_id}] {p.title} ({p.progress}% - {len(p.completed_steps)}/5 steps)" for p in data["projects"]]
    choices.append("Cancel")

    selected = prompt_select("Select project to update:", choices)
    if not selected or selected == "Cancel":
        return

    prj_id = selected.split("]")[0].replace("[", "").strip()
    target = next((p for p in data["projects"] if p.project_id == prj_id), None)
    if not target:
        return

    selected_steps = prompt_checkbox(
        "Check completed milestones (Space to toggle, Enter to save):",
        Project.MILESTONES,
        checked_items=target.completed_steps
    )
    if selected_steps is None:
        return

    target.update_milestones(selected_steps)

    if target.progress == 100:
        print_info("All 5 milestones completed (100%)!")
        earned = prompt_required_text("Enter Final Project Earned Score:", default_value="95")
        max_s = prompt_required_text("Enter Maximum Score:", default_value="100")
        target.set_earned_score(earned)
        target.set_max_score(max_s)
    else:
        target.set_earned_score(None)

    show_spinner("Calculating progress and updating project...")
    save_data(data)
    print_success(f"Project updated automatically! New Progress: {target.progress}% | Current Phase: {target.phase}")

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
    data["projects"] = [p for p in data["projects"] if p.project_id != prj_id]
    save_data(data)
    print_success("Project deleted successfully.")