# main
from rich.console import Console
from rich.table import Table
import questionary

from auth import login
from task_manager import get_all_tasks, get_user_tasks

console = Console()


def show_tasks(tasks):
    

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="TaskFlow - Tasks")

    table.add_column("ID", justify="center")
    table.add_column("Title")
    table.add_column("Assigned To")
    table.add_column("Status")
    table.add_column("Priority")

    for task in tasks:
        table.add_row(
            str(task.get("id", "")),
            str(task.get("title", "")),
            str(task.get("assigned_to", "")),
            str(task.get("status", "")),
            str(task.get("priority", "")),
        )

    console.print(table)


def main():
    console.print("[bold cyan]TASKFLOW - LOGIN TEST[/bold cyan]")

    while True:
        username = questionary.text("Username:").ask()

        if not username:
            console.print("[yellow]Username is required.[/yellow]")
            continue

        password = questionary.password("Password:").ask()

        if password is None:
            break

        user = login(username, password)

        if not user:
            console.print(
                "[red]Invalid username or password, "
                "or account is inactive.[/red]"
            )
            continue

        if not user.get("active", True):
            console.print("[red]Account is inactive.[/red]")
            continue

        role = user.get("role")

        if role == "admin":
            console.print("[green]Admin login successful.[/green]")
            tasks = get_all_tasks()

        elif role == "member":
            console.print("[green]Member login successful.[/green]")
            tasks = get_user_tasks(username)

        else:
            console.print("[red]Unknown user role.[/red]")
            continue

        show_tasks(tasks)

        choice = questionary.select(
            "What would you like to do?",
            choices=["Log Out", "Exit"],
        ).ask()

        if choice == "Exit" or choice is None:
            break

    console.print("[cyan]Test ended.[/cyan]")


if __name__ == "__main__":
    main()
