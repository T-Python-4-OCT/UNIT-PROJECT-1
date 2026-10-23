from datetime import date
from data_manager import load_data, save_data
from group_manager import get_group_by_id


TASKS_FILE = "tasks.json"
USERS_FILE = "users.json"

VALID_PRIORITIES = ["Low", "Medium", "High"]


def create_task(
    title,
    description,
    assigned_to,
    priority,
    due_date,
    created_by,
    group_id=None,
):
    '''Create a new task with validation.'''
    from datetime import date

    title = title.strip()
    description = description.strip()
    assigned_to = assigned_to.strip()

    if not title:
        return False, "Task title cannot be empty."

    if priority not in ["Low", "Medium", "High"]:
        return False, "Invalid priority."

    try:
        parsed_due_date = date.fromisoformat(due_date)
    except (ValueError, TypeError):
        return False, "Invalid due date. Use YYYY-MM-DD."

    if parsed_due_date < date.today():
        return False, "Due date cannot be in the past."

    group = get_group_by_id(group_id)

    if group is None:
        return False, "Group not found."

    from data_manager import load_data, save_data

    users = load_data("users.json")

    member = next(
        (
            user for user in users
            if user.get("username", "").lower() == assigned_to.lower()
            and user.get("role") == "member"
            and user.get("active", True)
        ),
        None,
    )

    if member is None:
        return False, "Active team member not found."

    group_members = group.get("members", [])

    if not any(
        name.lower() == member["username"].lower()
        for name in group_members
    ):
        return False, "The assigned member does not belong to this group."

    tasks = load_data("tasks.json")

    task_id = max(
        (task.get("id", 0) for task in tasks),
        default=0,
    ) + 1

    new_task = {
        "id": task_id,
        "title": title,
        "description": description,
        "assigned_to": member["username"],
        "group_id": group["id"],
        "group_name": group["name"],
        "priority": priority,
        "due_date": due_date,
        "status": "To Do",
        "created_by": created_by,
        "progress": 0,
    }

    tasks.append(new_task)
    save_data("tasks.json", tasks)

    return True, f"Task created successfully. ID: {task_id}"



def get_all_tasks():
    """Return all tasks."""

    return load_data(TASKS_FILE)


def get_user_tasks(username):
    """Return tasks assigned to a specific user."""

    tasks = load_data(TASKS_FILE)

    return [
        task for task in tasks
        if task.get("assigned_to", "").lower() == username.lower()
    ]


def update_task(
    task_id,
    title=None,
    description=None,
    assigned_to=None,
    priority=None,
    due_date=None,
):
    '''Update an existing task with validation.'''
    from datetime import date
    from data_manager import load_data, save_data
    from group_manager import get_group_by_id

    tasks = load_data("tasks.json")

    task = next(
        (item for item in tasks if item.get("id") == task_id),
        None,
    )

    if task is None:
        return False, "Task not found."

    if title is not None:
        title = title.strip()

        if not title:
            return False, "Task title cannot be empty."

    if description is not None:
        description = description.strip()

    if priority is not None:
        if priority not in ["Low", "Medium", "High"]:
            return False, "Invalid priority."

    if due_date is not None:
        try:
            parsed_due_date = date.fromisoformat(due_date)
        except (ValueError, TypeError):
            return False, "Invalid due date. Use YYYY-MM-DD."

        if parsed_due_date < date.today():
            return False, "Due date cannot be in the past."

    if assigned_to is not None:
        assigned_to = assigned_to.strip()

        if not assigned_to:
            return False, "Assigned username cannot be empty."

        users = load_data("users.json")

        member = next(
            (
                user for user in users
                if user.get("username", "").lower()
                == assigned_to.lower()
                and user.get("role") == "member"
                and user.get("active", True)
            ),
            None,
        )

        if member is None:
            return False, "Active team member not found."

        group_id = task.get("group_id")

        if group_id is not None:
            group = get_group_by_id(group_id)

            if group is None:
                return False, "Task group not found."

            group_members = group.get("members", [])

            if not any(
                name.lower() == member["username"].lower()
                for name in group_members
            ):
                return False, (
                    "Cannot assign this task to someone "
                    "outside its group."
                )

        assigned_to = member["username"]

    if title is not None:
        task["title"] = title

    if description is not None:
        task["description"] = description

    if assigned_to is not None:
        task["assigned_to"] = assigned_to

    if priority is not None:
        task["priority"] = priority

    if due_date is not None:
        task["due_date"] = due_date

    save_data("tasks.json", tasks)

    return True, "Task updated successfully."



def delete_task(task_id):
    """Delete a task by its ID."""

    tasks = load_data(TASKS_FILE)

    for index, task in enumerate(tasks):
        if task.get("id") == task_id:
            tasks.pop(index)
            save_data(TASKS_FILE, tasks)
            return True, "Task deleted successfully."

    return False, "Task not found."
