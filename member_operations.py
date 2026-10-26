import questionary
from rich.console import Console
from rich.table import Table

from task_manager import get_user_tasks
from tracking import (
    update_progress,
    submit_for_review,
    get_task_history,
)
from reports import get_member_report
from group_manager import get_all_groups, get_group_members


console = Console()


class MemberOperations:

    def __init__(self, user):
        self.user = user
        self.username = user["username"]

    def ask_int(self, message, minimum=None, maximum=None):
        while True:
            answer = questionary.text(message).ask()

            if answer is None:
                return None

            try:
                number = int(answer)

                if minimum is not None and number < minimum:
                    console.print(
                        f"[red]Enter a number greater than or equal to {minimum}.[/red]"
                    )
                    continue

                if maximum is not None and number > maximum:
                    console.print(
                        f"[red]Enter a number less than or equal to {maximum}.[/red]"
                    )
                    continue

                return number

            except ValueError:
                console.print("[red]Please enter a valid integer.[/red]")

    def show_my_tasks(self):
        '''Display tasks assigned to the logged-in member.'''
        tasks = get_user_tasks(self.username)

        if not tasks:
            console.print("[yellow]You have no assigned tasks.[/yellow]")
            return

        table = Table(title="My Tasks")
        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Priority")
        table.add_column("Status")
        table.add_column("Progress")

        for task in tasks:
            table.add_row(
                str(task.get("id", "")),
                task.get("title", ""),
                task.get("priority", ""),
                task.get("status", ""),
                f'{task.get("progress", 0)}%',
            )

        console.print(table)

    def update_my_task_progress(self):
        '''Update the progress of a task assigned to the logged-in member.'''
        tasks = get_user_tasks(self.username)

        if not tasks:
            console.print("[yellow]You have no tasks to update.[/yellow]")
            return

        self.show_my_tasks()

        task_id = self.ask_int("Enter the task ID:")
        if task_id is None:
            return

        task = next(
            (t for t in tasks if str(t.get("id")) == str(task_id)),
            None,
        )

        if task is None:
            console.print("[red]Task not found in your assigned tasks.[/red]")
            return

        progress = self.ask_int(
            "Enter progress percentage (0-100):",
            minimum=0,
            maximum=100,
        )

        if progress is None:
            return

        note = questionary.text("Enter a progress note:").ask()
        if note is None:
            return

        success, message = update_progress(
            task_id,
            self.username,
            progress,
            note,
        )

        console.print(
            f"[green]{message}[/green]"
            if success
            else f"[red]{message}[/red]"
        )

    def submit_my_task_for_review(self):
        '''Submit a task for review that is assigned to the logged-in member.'''
        tasks = get_user_tasks(self.username)

        if not tasks:
            console.print("[yellow]You have no tasks to submit.[/yellow]")
            return

        self.show_my_tasks()

        task_id = self.ask_int("Enter the task ID to submit for review:")
        if task_id is None:
            return

        task = next(
            (t for t in tasks if str(t.get("id")) == str(task_id)),
            None,
        )

        if task is None:
            console.print("[red]Task not found in your assigned tasks.[/red]")
            return

        note = questionary.text("Enter submission notes:").ask()
        if note is None:
            return

        success, message = submit_for_review(
            task_id,
            self.username,
            note,
        )

        console.print(
            f"[green]{message}[/green]"
            if success
            else f"[red]{message}[/red]"
        )

    def show_my_task_history(self):
        '''Display the history of a task assigned to the logged-in member.'''
        tasks = get_user_tasks(self.username)

        if not tasks:
            console.print("[yellow]You have no tasks to view.[/yellow]")
            return

        self.show_my_tasks()

        task_id = self.ask_int("Enter the task ID:")
        if task_id is None:
            return

        task = next(
            (t for t in tasks if str(t.get("id")) == str(task_id)),
            None,
        )

        if task is None:
            console.print("[red]Task not found in your assigned tasks.[/red]")
            return

        history = get_task_history(task_id)

        if not history:
            console.print("[yellow]No history found for this task.[/yellow]")
            return

        table = Table(title=f"Task History: {task.get('title', '')}")
        table.add_column("Date")
        table.add_column("User")
        table.add_column("Action")
        table.add_column("Progress")
        table.add_column("Note")

        for item in history:
            table.add_row(
                str(item.get("timestamp", "")).replace("T", " ")[:16],
                str(item.get("username", "")),
                str(item.get("action", "")),
                f'{item.get("progress", "")}%',
                str(item.get("note", "")),
            )

        console.print(table)

    def show_my_report(self):
        '''Display a summary report for the logged-in member.'''
        report = get_member_report(self.username)

        if not report:
            console.print("[yellow]No report available.[/yellow]")
            return

        table = Table(title="My Report")
        table.add_column("Metric")
        table.add_column("Value")

        for key, value in report.items():
            table.add_row(str(key), str(value))

        console.print(table)

    def show_my_groups(self):
        '''Display groups that the logged-in member belongs to.'''
        groups = get_all_groups()
        my_groups = []

        for group in groups:
            members = get_group_members(group.get("id"))

            if any(
                member.get("username") == self.username
                if isinstance(member, dict)
                else member == self.username
                for member in members
            ):
                my_groups.append(group)

        if not my_groups:
            console.print("[yellow]You are not a member of any group.[/yellow]")
            return

        table = Table(title="My Groups")
        table.add_column("Group ID")
        table.add_column("Group Name")
        table.add_column("Description")

        for group in my_groups:
            table.add_row(
                str(group.get("id", "")),
                group.get("name", ""),
                group.get("description", ""),
            )

        console.print(table)
