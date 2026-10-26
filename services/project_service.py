import uuid
from datetime import datetime
import questionary
from questionary import Choice, Style
from rich.table import Table
from rich.panel import Panel
from models.classes import Project
from storage import save_data
import utils
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_select,
    prompt_required_text
)


def confirm_delete_action(item_name):
    delete_style = Style([
        ("qmark", "fg:yellow bold"),
        ("question", "fg:white bold"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "bold"),
    ])
    choices = [
        Choice(title=[("fg:white", f"No, keep '{item_name}' (Cancel)")], value=False),
        Choice(title=[("fg:ansired bold", f"Yes, Delete '{item_name}' Successfully")], value=True),
    ]
    return questionary.select(
        f"Are you sure you want to delete '{item_name}'?",
        choices=choices,
        style=delete_style
    ).ask()


def ask_valid_score(prompt_text, max_val):
    while True:
        val = prompt_required_text(prompt_text, default_value=str(int(max_val)))
        try:
            score = float(val)
            if 0.0 <= score <= max_val:
                return score
            print_error(f"Score must be between 0 and {max_val:.0f}.")
        except ValueError:
            print_error("Please enter a valid number.")


def format_steps_vertical(project):
    if not project.steps:
        return "[dim]No steps defined[/dim]"
    lines = []
    for idx, s in enumerate(project.steps, 1):
        name = s.get("name", f"Step {idx}")
        weight = s.get("weight", 0)
        e_pts = s.get("earned_points")
        m_pts = s.get("max_points", 0)

        if s.get("completed"):
            pts_str = f"{e_pts:.1f}/{m_pts:.0f} pts" if e_pts is not None else f"{m_pts:.0f}/{m_pts:.0f} pts"
            lines.append(f"[bold green]✔ {idx}. {name} ({weight}% | {pts_str})[/bold green]")
        else:
            lines.append(f"[dim]○ {idx}. {name} ({weight}%)[/dim]")
    return "\n".join(lines)


def view_projects(data):
    projects = data.get("projects", [])
    subjects = data.get("subjects", [])
    if not projects:
        print_info("No academic projects found.")
        return

    sub_map = {s.subject_id: f"{s.code} - {s.name}" for s in subjects}
    table = Table(title="Academic Projects & Milestones", show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Project Title", width=22)
    table.add_column("Subject", width=18)
    table.add_column("Deadline", width=12)
    table.add_column("Steps Breakdown", width=36)
    table.add_column("Overall Progress", width=24)
    table.add_column("Total Score", width=14)

    for idx, p in enumerate(projects, 1):
        sub_label = sub_map.get(p.subject_id, "Unknown")
        steps_str = format_steps_vertical(p)
        prog_bar = utils.render_progress_bar(p.progress)

        if p.earned_score is not None and p.max_score:
            pct = (p.earned_score / p.max_score) * 100
            sc_color = "green" if pct >= 85 else ("yellow" if pct >= 60 else "red")
            score_str = f"[{sc_color}]{p.earned_score:.1f}/{p.max_score:.0f}\n({pct:.0f}%)[/{sc_color}]"
        else:
            score_str = f"[dim]-- / {p.max_score:.0f}[/dim]"

        table.add_row(
            str(idx),
            f"[bold]{p.title}[/bold]\n[dim]Phase: {p.phase}[/dim]",
            sub_label,
            p.deadline,
            steps_str,
            prog_bar,
            score_str
        )

    console.print(table)


def add_project(data):
    subjects = data.get("subjects", [])
    if not subjects:
        print_error("Please add a subject first before creating a project.")
        return None

    print_header(
        "Create Academic Project",
        "Tip: Type 'b' to go back, or 'm' to return to Main Menu"
    )

    selected_sub = None
    title = ""
    deadline = "2026-12-15"
    num_steps = 4
    steps = []

    stage = 1
    while True:
        # 1. اختيار المادة أولاً
        if stage == 1:
            sub_choices = [f"{s.code} - {s.name}" for s in subjects]
            sub_choices.append("⬅ Back to Projects Menu")
            sub_choices.append("🏠 Return to Main Menu")

            sub_choice = prompt_select("Step 1/5 — Select Subject First:", sub_choices)
            if not sub_choice or "Back to Projects Menu" in sub_choice:
                return None
            if "Return to Main Menu" in sub_choice:
                return "MAIN_MENU"

            selected_sub = subjects[sub_choices.index(sub_choice)]
            stage = 2

        # 2. إدخال عنوان المشروع ثانياً
        elif stage == 2:
            raw_title = prompt_required_text(
                f"Step 2/5 — Enter Project Title for {selected_sub.code} (or 'b' = Back, 'm' = Main):",
                default_value=title
            ).strip()

            if raw_title.lower() == "b":
                stage = 1
                continue
            if raw_title.lower() == "m":
                return "MAIN_MENU"

            title = raw_title
            stage = 3

        # 3. إدخال موعد التسليم
        elif stage == 3:
            raw_date = prompt_required_text(
                "Step 3/5 — Enter Deadline YYYY-MM-DD (or 'b' = Back, 'm' = Main):",
                default_value=deadline
            ).strip()

            if raw_date.lower() == "b":
                stage = 2
                continue
            if raw_date.lower() == "m":
                return "MAIN_MENU"

            try:
                datetime.strptime(raw_date, "%Y-%m-%d")
                deadline = raw_date
                stage = 4
            except ValueError:
                print_error("Invalid date format. Use YYYY-MM-DD.")

        # 4. عدد الخطوات
        elif stage == 4:
            raw_count = prompt_required_text(
                "Step 4/5 — Number of steps? (1 - 10) (or 'b' = Back, 'm' = Main):",
                default_value=str(num_steps)
            ).strip()

            if raw_count.lower() == "b":
                stage = 3
                continue
            if raw_count.lower() == "m":
                return "MAIN_MENU"

            try:
                val = int(raw_count)
                if 1 <= val <= 10:
                    num_steps = val
                    stage = 5
                else:
                    print_error("Enter a number between 1 and 10.")
            except ValueError:
                print_error("Enter a valid integer.")

        # 5. تفاصيل كل خطوة مع دعم التراجع
        elif stage == 5:
            steps = [None] * num_steps
            default_per_step = 100 // num_steps
            i = 0

            while i < num_steps:
                used_weight = sum(s["weight"] for s in steps[:i] if s is not None)
                remaining_weight = max(0, 100 - used_weight)

                console.print(
                    f"\n[bold cyan]--- Project Step {i + 1} of {num_steps} "
                    f"(Remaining Weight: {remaining_weight}%) ---[/bold cyan]"
                )

                prev_name = steps[i]["name"] if steps[i] else ""
                s_name = prompt_required_text(
                    f"Step {i+1} Name (or 'b' = Previous Step, 'm' = Main Menu):",
                    default_value=prev_name
                ).strip()

                if s_name.lower() == "b":
                    if i == 0:
                        stage = 4
                        break
                    else:
                        i -= 1
                        continue
                if s_name.lower() == "m":
                    return "MAIN_MENU"

                if i == num_steps - 1 and remaining_weight > 0:
                    suggested_w = remaining_weight
                else:
                    suggested_w = min(default_per_step, remaining_weight) if remaining_weight > 0 else 10

                prev_w = steps[i]["weight"] if steps[i] else suggested_w
                raw_w = prompt_required_text(
                    f"Step {i+1} Percentage (%) [Remaining: {remaining_weight}%] (or 'b' = Back):",
                    default_value=str(prev_w)
                ).strip()

                if raw_w.lower() == "b":
                    continue
                if raw_w.lower() == "m":
                    return "MAIN_MENU"

                try:
                    weight = max(1, min(100, int(raw_w)))
                except ValueError:
                    weight = suggested_w

                steps[i] = {
                    "name": s_name,
                    "weight": weight,
                    "max_points": float(weight),
                    "earned_points": None,
                    "completed": False
                }

                next_label = (
                    f"✔ Save & Create Project '{title}'"
                    if i == num_steps - 1
                    else f"✔ Confirm Step {i + 1} & Proceed"
                )
                nav_action = prompt_select(
                    f"Step {i + 1} ('{s_name}' - {weight}%) Ready:",
                    [
                        next_label,
                        f"✏ Edit Step {i + 1} Again",
                        "⬅ Back to Previous Step",
                        "🏠 Return to Main Menu"
                    ]
                )

                if not nav_action or "Return to Main Menu" in nav_action:
                    return "MAIN_MENU"
                elif "Edit Step" in nav_action:
                    continue
                elif "Back to Previous Step" in nav_action:
                    if i == 0:
                        stage = 4
                        break
                    else:
                        i -= 1
                        continue
                else:
                    i += 1

            if stage == 5 and i == num_steps:
                break

    new_project = Project(
        project_id=str(uuid.uuid4())[:8],
        title=title,
        subject_id=selected_sub.subject_id,
        deadline=deadline,
        steps=steps
    )
    data["projects"].append(new_project)
    save_data(data)
    print_success(f"Project '{title}' created successfully for {selected_sub.code}!")
    return None


def update_project_steps(data):
    projects = data.get("projects", [])
    if not projects:
        print_info("No projects available to update.")
        return None

    while True:
        proj_choices = [f"{p.title} (Progress: {p.progress}%)" for p in projects]
        proj_choices.append("⬅ Back to Projects Menu")
        proj_choices.append("🏠 Return to Main Menu")
        p_choice = prompt_select("Select a Project to manage its steps:", proj_choices)

        if not p_choice or "Back to Projects Menu" in p_choice:
            return None
        if "Return to Main Menu" in p_choice:
            return "MAIN_MENU"

        project = projects[proj_choices.index(p_choice)]

        while True:
            console.print()
            console.print(Panel(
                f"[bold cyan]{project.title}[/bold cyan] — Current Phase: [yellow]{project.phase}[/yellow]\n"
                f"Overall Progress: {utils.render_progress_bar(project.progress)}\n\n"
                f"{format_steps_vertical(project)}",
                title="Project Milestones Status",
                border_style="cyan"
            ))

            step_choices = []
            for idx, s in enumerate(project.steps):
                status_icon = "✔ Done" if s.get("completed") else "○ Pending"
                step_choices.append(f"Step {idx + 1}: {s['name']} ({s['weight']}%) [{status_icon}]")
            step_choices.append("⬅ Back to Project Selection")
            step_choices.append("🏠 Return to Main Menu")

            s_choice = prompt_select("Select a step to toggle/grade:", step_choices)
            if not s_choice or "Back to Project Selection" in s_choice:
                break
            if "Return to Main Menu" in s_choice:
                return "MAIN_MENU"

            step_idx = step_choices.index(s_choice)
            step = project.steps[step_idx]

            if not step.get("completed"):
                action = prompt_select(
                    f"Mark '{step['name']}' ({step['weight']}%) as completed?",
                    [
                        f"1. Complete with Full Score ({step['max_points']:.0f}/{step['max_points']:.0f})",
                        f"2. Complete with Custom Score (out of {step['max_points']:.0f})",
                        "⬅ Back to Steps List"
                    ]
                )
                if action and "1." in action:
                    project.complete_step(step_idx, earned_points=step["max_points"])
                    save_data(data)
                    print_success(f"Step '{step['name']}' completed successfully!")
                elif action and "2." in action:
                    pts = ask_valid_score(
                        f"Enter score for '{step['name']}' (0 - {step['max_points']:.0f}):",
                        max_val=float(step["max_points"])
                    )
                    project.complete_step(step_idx, earned_points=pts)
                    save_data(data)
                    print_success(f"Step '{step['name']}' completed successfully with score {pts:.1f}!")
            else:
                confirm = prompt_select(
                    f"Step '{step['name']}' is already completed. Revert to Pending?",
                    ["Yes, revert to Pending", "⬅ No, keep as Completed"]
                )
                if confirm and "Yes" in confirm:
                    project.uncomplete_step(step_idx)
                    save_data(data)
                    print_info(f"Step '{step['name']}' reverted to pending.")


def delete_project(data):
    projects = data.get("projects", [])
    if not projects:
        print_info("No projects available to delete.")
        return

    choices = [f"{p.title} ({p.progress}%)" for p in projects]
    choices.append("⬅ Cancel")
    choice = prompt_select("Select Project to delete:", choices)

    if not choice or "Cancel" in choice:
        return

    idx = choices.index(choice)
    target = projects[idx]

    if confirm_delete_action(target.title):
        projects.pop(idx)
        save_data(data)
        print_success(f"Project '{target.title}' has been deleted successfully.")
    else:
        print_info("Deletion cancelled.")


def manage_projects_menu(data):
    while True:
        print_header("Manage Academic Projects", "Track project milestones and weights")
        choices = [
            "1. View All Projects",
            "2. Create New Project",
            "3. Update Project Steps & Progress",
            "4. Delete Project",
            "5. Back to Main Menu"
        ]
        choice = prompt_select("Projects Menu:", choices)

        if not choice or "5." in choice:
            break
        elif "1." in choice:
            view_projects(data)
        elif "2." in choice:
            res = add_project(data)
            if res == "MAIN_MENU":
                break
        elif "3." in choice:
            res = update_project_steps(data)
            if res == "MAIN_MENU":
                break
        elif "4." in choice:
            delete_project(data)