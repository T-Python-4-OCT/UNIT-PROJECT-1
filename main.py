import questionary
from rich.console import Console

from auth import login
from user_manager import create_user, get_all_users
from admin_operations import AdminOperations
from member_operations import MemberOperations
from dashboard import show_admin_dashboard

console = Console()


def setup_first_admin():
    """Create the first administrator account if no users exist."""
    users = get_all_users()

    if users:
        return

    console.print(
        "[yellow]No users found. Create the first administrator account.[/yellow]"
    )

    username = questionary.text("Username:").ask()
    if not username:
        return

    password = questionary.password("Password:").ask()
    if not password:
        return

    success, message = create_user(
        username=username,
        password=password,
        role="admin",
    )

    if success:
        console.print(f"[green]{message}[/green]")
    else:
        console.print(f"[red]{message}[/red]")


def show_with_exit(title, display_function):
    """Display information, then wait for the user to select Exit."""
    display_function()

    questionary.select(
        title,
        choices=["Exit"],
    ).ask()


def admin_submenu(title, options, admin):
    """Display an administrator section menu."""
    while True:
        choice = questionary.select(
            title,
            choices=options + ["Back to Main Menu"],
        ).ask()

        if choice is None or choice == "Back to Main Menu":
            return

        elif choice == "View Users":
            show_with_exit(
                "Users - Select Exit to return",
                admin.show_users,
            )

        elif choice == "Add User":
            admin.add_user()

        elif choice == "Change Status":
            admin.change_user_status()

        elif choice == "Create Task":
            admin.create_new_task()

        elif choice == "View All Tasks":
            show_with_exit(
                "All Tasks - Select Exit to return",
                admin.show_all_tasks,
            )

        elif choice == "Edit Task":
            admin.edit_existing_task()

        elif choice == "Delete Task":
            admin.delete_existing_task()

        elif choice == "Review Tasks":
            admin.review_pending_tasks()

        elif choice == "Create Groups":
            admin.create_work_group()

        elif choice == "View Groups":
            show_with_exit(
                "Groups - Select Exit to return",
                admin.show_groups,
            )

        elif choice == "Manage Members":
            manage_group_members(admin)


def manage_group_members(admin):
    """Manage members inside work groups."""
    while True:
        choice = questionary.select(
            "Manage Group Members:",
            choices=[
                "Add Group Member",
                "Remove Group Member",
                "Back to Group Management",
            ],
        ).ask()

        if choice is None or choice == "Back to Group Management":
            return

        elif choice == "Add Group Member":
            admin.add_group_member()

        elif choice == "Remove Group Member":
            admin.remove_group_member()


def admin_menu(user):
    """Display the administrator main menu."""
    admin = AdminOperations(user)

    while True:
        show_admin_dashboard()

        choice = questionary.select(
            "Administrator Main Menu:",
            choices=[
                "User Management",
                "Task Management",
                "Group Management",
                "Reports",
                "Log Out",
            ],
        ).ask()

        if choice is None or choice == "Log Out":
            break

        elif choice == "User Management":
            admin_submenu(
                "User Management:",
                [
                    "View Users",
                    "Add User",
                    "Change Status",
                ],
                admin,
            )

        elif choice == "Task Management":
            admin_submenu(
                "Task Management:",
                [
                    "Create Task",
                    "View All Tasks",
                    "Edit Task",
                    "Delete Task",
                    "Review Tasks",
                ],
                admin,
            )

        elif choice == "Group Management":
            admin_submenu(
                "Group Management:",
                [
                    "Create Groups",
                    "View Groups",
                    "Manage Members",
                ],
                admin,
            )

        elif choice == "Reports":
            show_with_exit(
                "Reports - Select Exit to return",
                admin.show_reports,
            )


def member_menu(user):
    """Display the member menu."""
    member = MemberOperations(user)

    while True:
        choice = questionary.select(
            "Member Menu:",
            choices=[
                "View My Tasks",
                "Update Task Progress",
                "Submit Task for Review",
                "View Task History",
                "View My Report",
                "View My Groups",
                "Log Out",
            ],
        ).ask()

        if choice is None or choice == "Log Out":
            break

        elif choice == "View My Tasks":
            show_with_exit(
                "My Tasks - Select Exit to return",
                member.show_my_tasks,
            )

        elif choice == "Update Task Progress":
            member.update_my_task_progress()

        elif choice == "Submit Task for Review":
            member.submit_my_task_for_review()

        elif choice == "View Task History":
            show_with_exit(
                "Task History - Select Exit to return",
                member.show_my_task_history,
            )

        elif choice == "View My Report":
            show_with_exit(
                "My Report - Select Exit to return",
                member.show_my_report,
            )

        elif choice == "View My Groups":
            show_with_exit(
                "My Groups - Select Exit to return",
                member.show_my_groups,
            )


def main():
    """Start TaskFlow."""
    setup_first_admin()

    while True:
        choice = questionary.select(
            "TaskFlow - Task Management System",
            choices=[
                "Log In",
                "Exit",
            ],
        ).ask()

        if choice is None or choice == "Exit":
            console.print("[cyan]TaskFlow closed.[/cyan]")
            break

        username = questionary.text("Username:").ask()
        if not username:
            continue

        password = questionary.password("Password:").ask()
        if password is None:
            continue

        user = login(username, password)

        if not user:
            console.print(
                "[red]Invalid username or password, or account is inactive.[/red]"
            )
            continue

        if not user.get("active", True):
            console.print("[red]This account is inactive.[/red]")
            continue

        role = user.get("role")

        if role == "admin":
            admin_menu(user)

        elif role == "member":
            member_menu(user)

        else:
            console.print("[red]Unknown account role.[/red]")


if __name__ == "__main__":
    main()
