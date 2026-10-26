"""
services/task_service.py
Add, view, complete, and delete tasks.
"""
from datetime import date
from rich.table import Table
from models.classes import Task
from services.base_service import BaseService
from utils import (
    console,
    print_header,
    print_success,
    print_info,
    prompt_text,
    prompt_date,
    prompt_float_range,
    prompt_select,
    show_spinner
)


def format_task_score(earned, max_s):
    if earned is None or max_s is None or max_s <= 0:
        return "[dim]⏳ Pending[/dim]"

    pct = (earned / max_s) * 100
    if pct >= 85:
        color = "bold green"
    elif pct >= 70:
        color = "cyan"
    elif pct >= 60:
        color = "yellow"
    else:
        color = "bold red"

    return f"[{color}]{earned:g}/{max_s:g} ({pct:.0f}%)[/{color}]"


def format_priority(priority):
    if priority == "High":
        return "[bold red]🔴 High[/bold red]"
    elif priority == "Medium":
        return "[yellow]🟡 Medium[/yellow]"
    return "[green]🟢 Low[/green]"


def display_tasks_table(tasks, subjects):
    if not tasks:
        print_info("No tasks available.")
        return

    sub_map = {s.subject_id: s.code for s in subjects}

    table = Table(title=f"Academic Tasks (Total: {len(tasks)})", show_header=True, header_style="bold cyan")
    table.add_column("Task ID", width=10)
    table.add_column("Title", width=28)
    table.add_column("Course", width=10)
    table.add_column("Due Date", width=12)
    table.add_column("Priority", width=12)
    table.add_column("Status", width=16)
    table.add_column("Score", width=18)

    for t in tasks:
        course_code = sub_map.get(t.subject_id, "N/A")
        if t.status == "Completed":
            status_str = "[green]✅ Completed[/green]"
        else:
            status_str = f"[yellow]⏳ {t.status}[/yellow]"

        table.add_row(
            t.task_id,
            t.title,
            f"[bold]{course_code}[/bold]",
            t.due_date,
            format_priority(t.priority),
            status_str,
            format_task_score(t.earned_score, t.max_score)
        )

    console.print()
    console.print(table)


class TaskService(BaseService):
    section_title = "📝 Manage Tasks & Assignments"
    section_subtitle = "View, add, complete, or delete your tasks"
    menu_options = [
        ("📋 View All Tasks", "view_all"),
        ("➕ Add New Task", "add"),
        ("✅ Mark Task as Completed", "complete"),
        ("🗑️  Delete Task", "delete"),
    ]

    def view_all(self):
        print_header("📋 All Tasks", "List of assignments and grades")
        show_spinner("Loading tasks...")
        display_tasks_table(self.data["tasks"], self.data["subjects"])

    def add(self):
        print_header("➕ Add New Task", "Create a new assignment")

        subject = self.select_subject()
        if not subject:
            return

        title = prompt_text("📝 Task Title:")
        description = prompt_text("📄 Description:")
        due_date = prompt_date("📅 Due Date (YYYY-MM-DD):", default_value=str(date.today()))
        priority = prompt_select("🚦 Priority:", ["High", "Medium", "Low"]) or "Medium"

        new_task = Task(self.next_id("tasks", "TSK", "task_id"), title, description,
                        subject.subject_id, due_date, priority)

        show_spinner("Saving task...")
        self.data["tasks"].append(new_task)
        self.save()
        print_success(f"Task '{title}' added successfully.")

    def complete(self):
        print_header("✅ Complete Task", "Update task status and record score")

        pending_tasks = [t for t in self.data["tasks"] if t.status != "Completed"]
        if not pending_tasks:
            print_info("No pending tasks available.")
            return

        task = self.select_item(pending_tasks, lambda t: f"[{t.task_id}] {t.title}", "Select task to complete:")
        if not task:
            return

        max_s = prompt_float_range("🎯 Maximum Score:", 0, None, default_value=100, min_exclusive=True)
        earned = prompt_float_range(f"⭐ Earned Score (0 - {max_s:g}):", 0, max_s,
                                    default_value=min(95, max_s))

        task.mark_completed(earned, max_s)

        show_spinner("Updating task...")
        self.save()
        print_success("Task marked as completed.")

    def delete(self):
        print_header("🗑️  Delete Task", "Remove a task")
        self.delete_record("tasks", lambda t: f"[{t.task_id}] {t.title}", "task")


def manage_tasks_menu(data):
    TaskService(data).run()