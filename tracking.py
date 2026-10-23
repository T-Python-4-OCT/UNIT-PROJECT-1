from datetime import datetime

from data_manager import load_data, save_data


TASKS_FILE = "tasks.json"
UPDATES_FILE = "updates.json"


def update_progress(task_id, username, progress, note):
    """Update progress on a task assigned to the current member."""

    if not isinstance(progress, int) or isinstance(progress, bool):
        return False, "Progress must be a whole number."

    if not 0 <= progress <= 100:
        return False, "Progress must be between 0 and 100."

    if not note.strip():
        return False, "Please provide a progress note."

    tasks = load_data(TASKS_FILE)

    task = next(
        (
            item for item in tasks
            if item.get("id") == task_id
            and item.get("assigned_to", "").lower() == username.lower()
        ),
        None
    )

    if task is None:
        return False, "Task not found or not assigned to you."

    if task.get("status") not in ["To Do", "In Progress", "Revision Required"]:
        return False, "This task cannot be updated in its current status."

    task["progress"] = progress
    task["status"] = "In Progress"

    save_data(TASKS_FILE, tasks)

    add_update(
        task_id,
        username,
        "Progress Updated",
        note.strip(),
        progress
    )

    return True, "Progress updated successfully."


def submit_for_review(task_id, username, note):
    """Submit a task to the manager for review."""

    tasks = load_data(TASKS_FILE)

    task = next(
        (
            item for item in tasks
            if item.get("id") == task_id
            and item.get("assigned_to", "").lower() == username.lower()
        ),
        None
    )

    if task is None:
        return False, "Task not found or not assigned to you."

    if task.get("status") not in ["In Progress", "Revision Required"]:
        return False, "Task cannot be submitted in its current status."

    if task.get("progress", 0) != 100:
        return False, "Progress must be 100% before review."

    if not note.strip():
        return False, "Please provide a submission note."

    task["status"] = "Pending Review"
    save_data(TASKS_FILE, tasks)

    add_update(
        task_id,
        username,
        "Submitted for Review",
        note.strip(),
        task.get("progress", 0)
    )

    return True, "Task submitted for manager review."


def review_task(task_id, manager_username, approved, feedback):
    """Approve a task or return it for revision."""

    tasks = load_data(TASKS_FILE)

    task = next(
        (item for item in tasks if item.get("id") == task_id),
        None
    )

    if task is None:
        return False, "Task not found."

    if task.get("status") != "Pending Review":
        return False, "Task is not waiting for review."

    if not isinstance(approved, bool):
        return False, "Approval must be True or False."

    if not feedback.strip():
        return False, "Please provide review feedback."

    if approved:
        task["status"] = "Completed"
        task["progress"] = 100
        action = "Approved"
    else:
        task["status"] = "Revision Required"
        action = "Revision Required"

    save_data(TASKS_FILE, tasks)

    add_update(
        task_id,
        manager_username,
        action,
        feedback.strip(),
        task.get("progress", 0)
    )

    return True, (
        "Task approved and completed."
        if approved
        else "Task returned for revision."
    )


def add_update(task_id, username, action, note, progress):
    """Save an entry in the task history."""

    updates = load_data(UPDATES_FILE)

    updates.append({
        "task_id": task_id,
        "username": username,
        "action": action,
        "note": note,
        "progress": progress,
        "timestamp": datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
    })

    save_data(UPDATES_FILE, updates)


def get_task_history(task_id):
    """Return all updates associated with a task."""

    updates = load_data(UPDATES_FILE)

    return [
        update for update in updates
        if update.get("task_id") == task_id
    ]
