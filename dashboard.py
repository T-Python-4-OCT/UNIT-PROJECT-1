from datetime import date

from rich.console import Console, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
)

from task_manager import get_all_tasks
from group_manager import get_all_groups
from user_manager import get_all_users


console = Console()


def get_task_counts(tasks):
    """Calculate task statistics."""

    counts = {
        "total": len(tasks),
        "completed": 0,
        "in_progress": 0,
        "pending_review": 0,
        "overdue": 0,
    }

    for task in tasks:
        status = task.get("status", "").lower()

        if status == "completed":
            counts["completed"] += 1
        elif status == "in progress":
            counts["in_progress"] += 1
        elif "review" in status:
            counts["pending_review"] += 1

        try:
            due_date = date.fromisoformat(task.get("due_date", ""))
            if due_date < date.today() and status != "completed":
                counts["overdue"] += 1
        except (ValueError, TypeError):
            pass

    return counts


def make_stat_panel(title, value, color):
    """Create a compact statistics panel."""

    content = Text(
        str(value),
        style=f"bold {color}",
        justify="center",
    )

    return Panel(
        content,
        title=f"[bold]{title}[/bold]",
        border_style=color,
        padding=(0, 1),
        width=19,
        height=3,
    )


def show_admin_dashboard():
    """Display a compact admin dashboard."""

    tasks = get_all_tasks()
    groups = get_all_groups()
    users = get_all_users()

    counts = get_task_counts(tasks)

    completion_rate = (
        counts["completed"] / counts["total"] * 100
        if counts["total"] > 0
        else 0
    )

    active_members = sum(
        1 for user in users
        if user.get("role") == "member"
        and user.get("active", True)
    )

    console.clear()

    console.print(
        Panel(
            "[bold cyan]TASKFLOW[/bold cyan]  "
            "[white]ADMIN DASHBOARD[/white]",
            border_style="cyan",
            padding=(0, 1),
        )
    )

    console.print()

    summary_panels = [
        make_stat_panel(
            "Completion %",
            f"{completion_rate:.1f}%",
            "green",
        ),
        make_stat_panel("Total Tasks", counts["total"], "cyan"),
        make_stat_panel("Completed", counts["completed"], "green"),
        make_stat_panel("In Progress", counts["in_progress"], "yellow"),
        make_stat_panel("Pending Review", counts["pending_review"], "magenta"),
        make_stat_panel("Overdue", counts["overdue"], "red"),
        make_stat_panel("Active Members", active_members, "blue"),
    ]

    console.print(
        Columns(
            summary_panels,
            equal=True,
            expand=False,
            padding=(0, 1),
        )
    )

    console.print()
    console.print("[bold cyan]GROUP PERFORMANCE[/bold cyan]")
    console.print()

    if not groups:
        console.print("[yellow]No work groups have been created yet.[/yellow]")
        return

    for group in groups:
        group_id = group.get("id")

        group_tasks = [
            task for task in tasks
            if task.get("group_id") == group_id
        ]

        group_counts = get_task_counts(group_tasks)

        member_count = len(group.get("members", []))
        total = group_counts["total"]
        completed = group_counts["completed"]

        completion_rate = (
            completed / total * 100 if total else 0
        )

        progress = Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=20),
            TextColumn("{task.percentage:>3.0f}%"),
            expand=False,
            console=console,
        )

        progress.add_task(
            group.get("name", "Unnamed Group"),
            total=100,
            completed=completion_rate,
        )

        details = Text()
        details.append(f"Members: {member_count}  ")
        details.append(f"Tasks: {total}  ")
        details.append(f"Done: {completed}  ", style="green")
        details.append(
            f"Active: {group_counts['in_progress']}  ",
            style="yellow",
        )
        details.append(
            f"Review: {group_counts['pending_review']}  ",
            style="magenta",
        )
        details.append(
            f"Overdue: {group_counts['overdue']}",
            style="red",
        )

        console.print(
            Panel(
                Group(progress, details),
                title=f"[bold]{group.get('name', 'Unnamed Group')}[/bold]",
                border_style="blue",
                padding=(0, 1),
            )
        )
# Test the dashboard display
if __name__ == "__main__":
    show_admin_dashboard()
