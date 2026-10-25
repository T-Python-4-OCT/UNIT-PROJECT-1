import questionary
from rich.console import Console
from rich.table import Table

from user_manager import (
    create_user,
    get_all_users,
    set_user_status,
)
from task_manager import (
    create_task,
    get_all_tasks,
    update_task,
    delete_task,
)
from tracking import (
    review_task,
    get_task_history,
)
from reports import (
    get_task_statistics,
    get_all_member_reports,
    get_overdue_tasks,
)
from group_manager import (
    create_group,
    get_all_groups,
    get_group_by_id,
    add_member_to_group,
    remove_member_from_group,
    get_group_members,
)

console = Console()


class AdminOperations:

    def __init__(self, user):
        self.user = user

    def ask_int(self, message):
        value = questionary.text(message).ask()

        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
            return None

    def show_users(self):
        '''Display all users in a table format.'''
        users = get_all_users()

        if not users:
            console.print("[yellow]No users found.[/yellow]")
            return

        table = Table(title="Users")
        table.add_column("Username")
        table.add_column("Role")
        table.add_column("Status")

        for user in users:
            status = (
                "Active"
                if user.get("active", True)
                else "Inactive"
            )
            table.add_row(
                user["username"],
                user["role"],
                status,
            )

        console.print(table)

    def add_user(self):
        '''Add a new user to the system.'''
        username = questionary.text("Enter username:").ask()
        if username is None:
            return

        password = questionary.password("Enter password:").ask()
        if password is None:
            return

        if not any(char.isupper() and char.isascii() for char in password):
            console.print("[red]Password must contain at least one uppercase English letter.[/red]")
            return

        role = questionary.select(
            "Select user role:",
            choices=["member", "admin"],
        ).ask()

        if role is None:
            return

        success, message = create_user(username, password, role)
        console.print(
            f"[green]{message}[/green]"
            if success else f"[red]{message}[/red]"
        )

    def change_user_status(self):
        '''Activate or deactivate a user account.'''
        self.show_users()

        username = questionary.text(
            "Enter username to activate/deactivate:"
        ).ask()

        if not username:
            return

        active = questionary.confirm(
            "Activate this user?"
        ).ask()

        if active is None:
            return

        success, message = set_user_status(username, active)
        console.print(
            f"[green]{message}[/green]"
            if success else f"[red]{message}[/red]"
        )

    def create_new_task(self):
        '''Create a new task and assign it to a group member.'''
        while True:
            groups = get_all_groups()

            if not groups:
                console.print(
                    "[yellow]No groups available. Create a group first.[/yellow]"
                )
                return

            group_choices = [
                questionary.Choice(
                    title=group["name"],
                    value=group["id"],
                )
                for group in groups
            ]

            group_id = questionary.select(
                "Select a group:",
                choices=group_choices,
            ).ask()

            if group_id is None:
                return

            group = get_group_by_id(group_id)

            if not group:
                console.print("[red]Group not found.[/red]")
                return

            members = get_group_members(group_id)

            member_choices = []

            for member in members:
                if isinstance(member, dict):
                    username = member.get("username")
                else:
                    username = member

                if username:
                    member_choices.append(
                        questionary.Choice(
                            title=str(username),
                            value=username,
                        )
                    )

            if not member_choices:
                console.print(
                    "[yellow]No members available in this group.[/yellow]"
                )
                return

            assigned_to = questionary.select(
                "Assign task to:",
                choices=member_choices,
            ).ask()

            if assigned_to is None:
                return

            title = questionary.text("Task title:").ask()

            if not title or not title.strip():
                console.print("[yellow]Task creation cancelled.[/yellow]")
                return

            description = questionary.text(
                "Task description:"
            ).ask()

            if description is None:
                return

            priority = questionary.select(
                "Select priority:",
                choices=["Low", "Medium", "High"],
            ).ask()

            if priority is None:
                return

            due_date = questionary.text(
                "Due date (YYYY-MM-DD):"
            ).ask()

            if due_date is None:
                return

            success, message = create_task(
                title=title.strip(),
                description=description,
                assigned_to=assigned_to,
                priority=priority,
                due_date=due_date,
                created_by=self.user["username"],
                group_id=group_id,
            )

            if success:
                console.print(f"[green]{message}[/green]")

                next_action = questionary.select(
                    "What would you like to do next?",
                    choices=[
                        "Create Another Task",
                        "Return to Main Menu",
                    ],
                ).ask()

                if next_action != "Create Another Task":
                    return

            else:
                console.print(f"[red]{message}[/red]")
                return


    def show_all_tasks(self):
        '''Display all tasks in a table format.'''
        tasks = get_all_tasks()

        if not tasks:
            console.print("[yellow]No tasks found.[/yellow]")
            return

        table = Table(title="All Tasks")
        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Group")
        table.add_column("Assigned To")
        table.add_column("Priority")
        table.add_column("Status")
        table.add_column("Progress")

        for task in tasks:
            table.add_row(
                str(task["id"]),
                task.get("title", ""),
                task.get("group_name", "N/A"),
                task.get("assigned_to", ""),
                task.get("priority", ""),
                task.get("status", ""),
                f'{task.get("progress", 0)}%',
            )

        console.print(table)

    def edit_existing_task(self):
        '''Edit an existing task's details.'''
        self.show_all_tasks()

        task_id = self.ask_int("Enter task ID to edit:")
        if task_id is None:
            return

        task = next(
            (
                item for item in get_all_tasks()
                if item.get("id") == task_id
            ),
            None,
        )

        if task is None:
            console.print("[red]Task not found.[/red]")
            return

        group_id = task.get("group_id")
        group = (
            get_group_by_id(group_id)
            if group_id is not None else None
        )

        if group_id is not None and group is None:
            console.print("[red]Task group not found.[/red]")
            return

        group_members = (
            group.get("members", [])
            if group is not None else None
        )

        active_members = [
            user["username"]
            for user in get_all_users()
            if user.get("role") == "member"
            and user.get("active", True)
            and (
                group_members is None
                or any(
                    name.lower() == user["username"].lower()
                    for name in group_members
                )
            )
        ]

        title = questionary.text(
            "New title (leave empty to keep current):"
        ).ask()
        if title is None:
            return

        description = questionary.text(
            "New description (leave empty to keep current):"
        ).ask()
        if description is None:
            return

        if not active_members:
            console.print(
                "[yellow]No active members available.[/yellow]"
            )
            return

        current_assignee = task.get("assigned_to")
        default_member = (
            current_assignee
            if current_assignee in active_members
            else active_members[0]
        )

        assigned_to = questionary.select(
            "Select assignee:",
            choices=active_members,
            default=default_member,
        ).ask()

        if assigned_to is None:
            return

        priority = questionary.select(
            "Select priority:",
            choices=["Low", "Medium", "High"],
            default=task.get("priority", "Medium"),
        ).ask()

        if priority is None:
            return

        due_date = questionary.text(
            "New due date (YYYY-MM-DD, leave empty to keep current):"
        ).ask()
        if due_date is None:
            return

        success, message = update_task(
            task_id,
            title=title or None,
            description=description or None,
            assigned_to=assigned_to,
            priority=priority,
            due_date=due_date or None,
        )

        console.print(
            f"[green]{message}[/green]"
            if success else f"[red]{message}[/red]"
        )

    def delete_existing_task(self):
        '''Delete an existing task from the system.'''
        self.show_all_tasks()

        task_id = self.ask_int("Enter task ID to delete:")
        if task_id is None:
            return

        confirm = questionary.confirm(
            f"Delete task {task_id}?"
        ).ask()

        if not confirm:
            return

        success, message = delete_task(task_id)
        console.print(
            f"[green]{message}[/green]"
            if success else f"[red]{message}[/red]"
        )

    def review_pending_tasks(self):
        '''Review tasks that are pending approval.'''
        pending_tasks = [
            task for task in get_all_tasks()
            if task.get("status") == "Pending Review"
        ]

        if not pending_tasks:
            console.print("[yellow]No tasks awaiting review.[/yellow]")
            return

        for task in pending_tasks:
            table = Table(
                title=f'Task Review: {task.get("title", "")}'
            )
            table.add_column("Field")
            table.add_column("Details")

            for label, key in [
                ("Task ID", "id"),
                ("Title", "title"),
                ("Description", "description"),
                ("Group", "group_name"),
                ("Assigned To", "assigned_to"),
                ("Priority", "priority"),
                ("Due Date", "due_date"),
                ("Status", "status"),
                ("Progress", "progress"),
            ]:
                value = task.get(key, "")
                if key == "progress":
                    value = f"{value}%"
                table.add_row(label, str(value))

            console.print(table)

            history = get_task_history(task["id"])

            history_table = Table(title="Member Updates and Notes")
            history_table.add_column("Date")
            history_table.add_column("User")
            history_table.add_column("Action")
            history_table.add_column("Progress")
            history_table.add_column("Note")

            for entry in history:
                timestamp = str(entry.get("timestamp", ""))

                history_table.add_row(
                    timestamp.replace("T", " ")[:16],
                    str(entry.get("username", "")),
                    str(entry.get("action", "")),
                    f'{entry.get("progress", 0)}%',
                    str(entry.get("note", "")),
                )

            console.print(history_table)

            action = questionary.select(
                "Review decision:",
                choices=["Approve", "Request Revision", "Skip"],
            ).ask()

            if action is None or action == "Skip":
                continue

            feedback = questionary.text(
                "Enter review feedback:"
            ).ask()

            if not feedback or not feedback.strip():
                console.print("[yellow]Feedback is required.[/yellow]")
                continue

            success, message = review_task(
                task["id"],
                self.user["username"],
                action == "Approve",
                feedback.strip(),
            )

            console.print(
                f"[green]{message}[/green]"
                if success else f"[red]{message}[/red]"
            )

    def show_reports(self):
        '''Display task statistics and member reports.'''
        stats = get_task_statistics()

        table = Table(title="Task Statistics")
        table.add_column("Metric")
        table.add_column("Value")

        table.add_row("Total Tasks", str(stats["total"]))
        table.add_row("Completed", str(stats["completed"]))
        table.add_row("In Progress", str(stats["in_progress"]))
        table.add_row("Pending Review", str(stats["pending_review"]))
        table.add_row("Overdue", str(stats["overdue"]))
        table.add_row(
            "Completion Rate",
            f'{stats["completion_rate"]:.1f}%',
        )
        console.print(table)

        reports = get_all_member_reports()

        if reports:
            member_table = Table(title="Member Reports")
            for column in [
                "Member", "Total", "Completed",
                "In Progress", "Overdue",
            ]:
                member_table.add_column(column)

            for report in reports:
                member_table.add_row(
                    report["username"],
                    str(report["total"]),
                    str(report["completed"]),
                    str(report["in_progress"]),
                    str(report["overdue"]),
                )

            console.print(member_table)

        overdue_tasks = get_overdue_tasks()

        if overdue_tasks:
            console.print("\n[bold red]Overdue Tasks[/bold red]")

            for task in overdue_tasks:
                console.print(
                    f'ID {task["id"]}: {task["title"]} '
                    f'— Due: {task["due_date"]}'
                )

    def create_work_group(self):
        '''Create a new work group.'''
        name = questionary.text("Group name:").ask()
        if name is None:
            return

        description = questionary.text("Group description:").ask()
        if description is None:
            return

        success, message = create_group(
            name,
            description,
            self.user["username"],
        )

        console.print(
            f"[green]{message}[/green]"
            if success else f"[red]{message}[/red]"
        )

    def show_groups(self):
        '''Display all work groups in a table format.'''
        groups = get_all_groups()

        if not groups:
            console.print("[yellow]No groups found.[/yellow]")
            return

        table = Table(title="Work Groups")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Members")

        for group in groups:
            table.add_row(
                str(group["id"]),
                group["name"],
                group.get("description", ""),
                ", ".join(group.get("members", [])) or "None",
            )

        console.print(table)

    def add_group_member(self):
        '''Add a member to an existing work group.'''
        self.show_groups()

        group_id = self.ask_int("Enter group ID:")
        if group_id is None:
            return

        username = questionary.text("Member username:").ask()
        if not username:
            return

        success, message = add_member_to_group(group_id, username)
        console.print(
            f"[green]{message}[/green]"
            if success else f"[red]{message}[/red]"
        )

    def remove_group_member(self):
        '''Remove a member from an existing work group.'''
        self.show_groups()

        group_id = self.ask_int("Enter group ID:")
        if group_id is None:
            return

        members = get_group_members(group_id)

        if not members:
            console.print(
                "[yellow]No members in this group, or group not found.[/yellow]"
            )
            return

        username = questionary.select(
            "Select member to remove:",
            choices=members,
        ).ask()

        if username is None:
            return

        success, message = remove_member_from_group(
            group_id,
            username,
        )

        console.print(
            f"[green]{message}[/green]"
            if success else f"[red]{message}[/red]"
        )
        
# Test the AdminOperations class
if __name__ == "__main__":
   admin = AdminOperations({"username": "admin", "role": "admin"})
   admin.show_users()
   admin.add_user()
   admin.create_new_task()
   admin.show_all_tasks()
   admin.add_group_member()