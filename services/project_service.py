"""
services/project_service.py
Manage course projects and track milestone steps.
"""
from rich.table import Table
from rich.panel import Panel
from models.classes import Project
from services.base_service import BaseService, BACK_LABEL
import utils
from utils import (
    console,
    print_header,
    print_success,
    print_info,
    prompt_select,
    prompt_text,
    prompt_date,
    prompt_int_range,
    prompt_float_range
)


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
            lines.append(f"[bold green]✅ {idx}. {name} ({weight}% | {pts_str})[/bold green]")
        else:
            lines.append(f"[dim]⬜ {idx}. {name} ({weight}%)[/dim]")
    return "\n".join(lines)


class ProjectService(BaseService):
    section_title = "🚀 Manage Academic Projects"
    section_subtitle = "Track project milestones and weights"
    menu_prompt = "Projects Menu:"
    menu_options = [
        ("📋 View All Projects", "view_all"),
        ("➕ Create New Project", "add"),
        ("🛠️  Update Project Steps & Progress", "update_steps"),
        ("🗑️  Delete Project", "delete"),
    ]

    def view_all(self):
        projects = self.data["projects"]
        if not projects:
            print_info("No academic projects found.")
            return

        sub_map = {s.subject_id: f"{s.code} - {s.name}" for s in self.data["subjects"]}
        table = Table(title="Academic Projects & Milestones", show_header=True, header_style="bold cyan", show_lines=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Project Title", width=22)
        table.add_column("Subject", width=18)
        table.add_column("Deadline", width=12)
        table.add_column("Steps Breakdown", width=36)
        table.add_column("Overall Progress", width=24)
        table.add_column("Total Score", width=14)

        for idx, p in enumerate(projects, 1):
            prog_bar = utils.render_progress_bar(p.progress)

            pct = p.get_percentage()
            if pct is not None:
                sc_color = "green" if pct >= 85 else ("yellow" if pct >= 60 else "red")
                score_str = f"[{sc_color}]{p.earned_score:.1f}/{p.max_score:.0f}\n({pct:.0f}%)[/{sc_color}]"
            else:
                score_str = f"[dim]-- / {p.max_score:.0f}[/dim]"

            table.add_row(
                str(idx),
                f"[bold]{p.title}[/bold]\n[dim]Phase: {p.phase}[/dim]",
                sub_map.get(p.subject_id, "Unknown"),
                p.deadline,
                format_steps_vertical(p),
                prog_bar,
                score_str
            )

        console.print(table)

    def add(self):
        print_header("➕ Create Academic Project", "Define your project and its milestone steps")

        subject = self.select_subject("Select Subject:")
        if not subject:
            return

        title = prompt_text("📝 Project Title:")
        deadline = prompt_date("📅 Final Deadline (YYYY-MM-DD):", default_value="2026-12-15")
        num_steps = prompt_int_range("🔢 Number of steps (1 - 10):", 1, 10, 4)

        steps = []
        remaining_weight = 100

        for i in range(1, num_steps + 1):
            console.print(f"\n[bold cyan]🔹 Step {i} of {num_steps} (Remaining Weight: {remaining_weight}%)[/bold cyan]")
            step_name = prompt_text(f"📌 Step {i} Name:")

            steps_left_after = num_steps - i
            if steps_left_after == 0:
                # Give the remaining weight to the last step so the total equals 100%
                weight = remaining_weight
                print_info(f"Last step automatically assigned the remaining weight ({weight}%).")
            else:
                max_weight = remaining_weight - steps_left_after
                default_weight = max(1, min(100 // num_steps, max_weight))
                weight = prompt_int_range(
                    f"⚖️  Step {i} Weight (%) [1 - {max_weight}]:",
                    1, max_weight, default_weight
                )

            remaining_weight -= weight
            steps.append({
                "name": step_name,
                "weight": weight,
                "max_points": float(weight),
                "earned_points": None,
                "completed": False
            })

        new_project = Project(
            project_id=self.next_id("projects", "PRJ", "project_id"),
            title=title,
            subject_id=subject.subject_id,
            deadline=deadline,
            steps=steps
        )
        self.data["projects"].append(new_project)
        self.save()
        print_success(f"Project '{title}' created for {subject.code} with {len(steps)} steps.")

    def update_steps(self):
        projects = self.data["projects"]
        if not projects:
            print_info("No projects available to update.")
            return

        project = self.select_item(
            projects,
            lambda p: f"[{p.project_id}] {p.title} (Progress: {p.progress}%)",
            "Select a project to update:"
        )
        if not project:
            return

        while True:
            console.print()
            console.print(Panel(
                f"[bold cyan]{project.title}[/bold cyan] — Current Phase: [yellow]{project.phase}[/yellow]\n"
                f"Overall Progress: {utils.render_progress_bar(project.progress)}\n\n"
                f"{format_steps_vertical(project)}",
                title="📊 Project Milestones Status",
                border_style="cyan"
            ))

            step_choices = []
            for idx, s in enumerate(project.steps):
                status_icon = "✅ Done" if s.get("completed") else "⬜ Pending"
                step_choices.append(f"Step {idx + 1}: {s['name']} ({s['weight']}%) [{status_icon}]")
            step_choices.append(BACK_LABEL)

            s_choice = prompt_select("Select a step to update:", step_choices)
            if not s_choice or s_choice == BACK_LABEL:
                break

            step_idx = step_choices.index(s_choice)
            step = project.steps[step_idx]
            max_pts = step["max_points"]

            if not step.get("completed"):
                action = prompt_select(
                    f"Mark '{step['name']}' ({step['weight']}%) as completed?",
                    [
                        f"1. 🏆 Complete with Full Score ({max_pts:.0f}/{max_pts:.0f})",
                        f"2. ✏️  Complete with Custom Score (out of {max_pts:.0f})",
                        "3. ❌ Cancel"
                    ]
                )
                if action and "1." in action:
                    project.complete_step(step_idx, earned_points=max_pts)
                    self.save()
                    print_success(f"Step '{step['name']}' marked as completed!")
                elif action and "2." in action:
                    pts = prompt_float_range(
                        f"⭐ Enter score for '{step['name']}' (0 - {max_pts:.0f}):",
                        0, float(max_pts), default_value=int(max_pts)
                    )
                    project.complete_step(step_idx, earned_points=pts)
                    self.save()
                    print_success(f"Step '{step['name']}' completed with score {pts:.1f}!")
            else:
                confirm = prompt_select(
                    f"Step '{step['name']}' is already completed. Revert to Pending?",
                    ["Yes, Revert", "No, Cancel"]
                )
                if confirm and "Yes" in confirm:
                    project.uncomplete_step(step_idx)
                    self.save()
                    print_info(f"Step '{step['name']}' reverted to pending.")

    def delete(self):
        print_header("🗑️  Delete Project", "Remove a project and all its steps")
        self.delete_record("projects", lambda p: f"[{p.project_id}] {p.title} ({p.progress}%)", "project")


def manage_projects_menu(data):
    ProjectService(data).run()