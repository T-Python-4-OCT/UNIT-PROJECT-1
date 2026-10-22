from datetime import date
from rich.table import Table
from models.classes import Task
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_required_text,
    prompt_select,
    show_spinner
)

def manage_tasks_menu(data):
    while True:
        print_header(
            "SECTION: Task Management",
            "View, add, complete, or delete your tasks"
        )
        choices = [
            "1. View All Tasks",
            "2. Add New Task",
            "3. Mark Task as Completed",
            "4. Delete Task",
            "5. Back to Main Menu"
        ]
        choice = prompt_select("Select an action:", choices)

        if choice is None or "5." in choice:
            break
        elif "1." in choice:
            view_all_tasks(data)
        elif "2." in choice:
            add_task(data)
        elif "3." in choice:
            complete_task(data)
        elif "4." in choice:
            delete_task(data)

def display_tasks_table(tasks, subjects):
    if not tasks:
        print_info("No tasks available.")
        return

    sub_map = {s.subject_id: s.code for s in subjects}

    table = Table(title=f"Academic Tasks (Total: {len(tasks)})", show_header=True, header_style="bold cyan")
    table.add_column("Task ID", width=10)
    table.add_column("Title", width=25)
    table.add_column("Course", width=12)
    table.add_column("Due Date", width=12)
    table.add_column("Priority", width=10)
    table.add_column("Status", width=14)
    table.add_column("Score", width=10)

    for t in tasks:
        course_code = sub_map.get(t.subject_id, "N/A")
        score_str = f"{t.earned_score}/{t.max_score}" if t.earned_score is not None else "-"
        status_color = "green" if t.status == "Completed" else "yellow"

        table.add_row(
            t.task_id,
            t.title,
            course_code,
            t.due_date,
            t.priority,
            f"[{status_color}]{t.status}[/{status_color}]",
            score_str
        )

    console.print()
    console.print(table)

def view_all_tasks(data):
    print_header("VIEW: All Tasks", "Complete list of assignments")
    show_spinner("Loading tasks...")
    display_tasks_table([Task(**t) if isinstance(t, dict) else t for t in data["tasks"]], data["subjects"])

def generate_next_task_id(tasks):
    max_num = 0
    for item in tasks:
        t_id = item.task_id if hasattr(item, "task_id") else item.get("task_id", "")
        if t_id.startswith("TSK-"):
            num_part = t_id.replace("TSK-", "")
            if num_part.isdigit():
                num = int(num_part)
                if num > max_num:
                    max_num = num
    return f"TSK-{max_num + 1:03d}"

def add_task(data):
    print_header("ACTION: Add New Task", "Create a new assignment")
    
    if not data["subjects"]:
        print_error("Please add at least one subject first.")
        return

    sub_choices = [f"[{s.subject_id}] {s.code} - {s.name}" for s in data["subjects"]]
    selected_sub_str = prompt_select("Select Course:", sub_choices)
    if not selected_sub_str:
        return

    sub_id = selected_sub_str.split("]")[0].replace("[", "").strip()

    title = prompt_required_text("Enter Task Title:")
    if not title:
        return

    description = prompt_required_text("Enter Description:") or ""
    due_date = prompt_required_text("Enter Due Date (YYYY-MM-DD):", default_value=str(date.today()))
    priority = prompt_select("Select Priority:", ["High", "Medium", "Low"]) or "Medium"

    new_id = generate_next_task_id(data["tasks"])
    new_task = Task(new_id, title, description, sub_id, due_date, priority)

    show_spinner("Saving task...")
    data["tasks"].append(new_task.to_dict())
    save_data(data)
    print_success(f"Task '{title}' added successfully.")

def complete_task(data):
    print_header("ACTION: Complete Task", "Update task status and score")
    
    pending_tasks = [t for t in data["tasks"] if (t.status if hasattr(t, "status") else t.get("status")) != "Completed"]
    if not pending_tasks:
        print_info("No pending tasks available.")
        return

    choices = [f"[{t.task_id if hasattr(t, 'task_id') else t.get('task_id')}] {t.title if hasattr(t, 'title') else t.get('title')}" for t in pending_tasks]
    choices.append("Cancel")

    selected = prompt_select("Select task to complete:", choices)
    if not selected or selected == "Cancel":
        return

    task_id = selected.split("]")[0].replace("[", "").strip()
    target_task = None
    for t in data["tasks"]:
        t_id = t.task_id if hasattr(t, "task_id") else t.get("task_id")
        if t_id == task_id:
            target_task = t
            break

    if not target_task:
        return

    earned = prompt_required_text("Enter Earned Score:", default_value="100")
    max_s = prompt_required_text("Enter Maximum Score:", default_value="100")

    if hasattr(target_task, "mark_completed"):
        target_task.mark_completed(earned, max_s)
    else:
        target_task["status"] = "Completed"
        target_task["earned_score"] = float(earned) if earned else 100.0
        target_task["max_score"] = float(max_s) if max_s else 100.0

    show_spinner("Updating task...")
    data["tasks"] = [t.to_dict() if hasattr(t, "to_dict") else t for t in data["tasks"]]
    save_data(data)
    print_success("Task marked as completed.")

def delete_task(data):
    print_header("ACTION: Delete Task", "Remove a task")
    if not data["tasks"]:
        print_info("No tasks available.")
        return

    choices = [f"[{t.task_id if hasattr(t, 'task_id') else t.get('task_id')}] {t.title if hasattr(t, 'title') else t.get('title')}" for t in data["tasks"]]
    choices.append("Cancel")

    selected = prompt_select("Select task to delete:", choices)
    if not selected or selected == "Cancel":
        return

    task_id = selected.split("]")[0].replace("[", "").strip()
    data["tasks"] = [t for t in data["tasks"] if (t.task_id if hasattr(t, "task_id") else t.get("task_id")) != task_id]
    save_data(data)
    print_success("Task deleted successfully.")