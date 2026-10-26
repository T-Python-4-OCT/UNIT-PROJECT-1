from datetime import date

from data_manager import load_data


TASKS_FILE = "tasks.json"
USERS_FILE = "users.json"


def get_task_statistics():
    """Return general task statistics."""

    tasks = load_data(TASKS_FILE)
    today = date.today()

    total = len(tasks)

    completed = sum(
        1 for task in tasks
        if task.get("status") == "Completed"
    )

    in_progress = sum(
        1 for task in tasks
        if task.get("status") == "In Progress"
    )

    pending_review = sum(
        1 for task in tasks
        if task.get("status") == "Pending Review"
    )

    overdue = sum(
        1 for task in tasks
        if task.get("status") != "Completed"
        and task.get("due_date")
        and task["due_date"] < today.isoformat()
    )

    completion_rate = (
        round((completed / total) * 100, 2)
        if total else 0
    )

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "pending_review": pending_review,
        "overdue": overdue,
        "completion_rate": completion_rate
    }


def get_member_report(username):
    """Return task statistics for one member."""

    tasks = load_data(TASKS_FILE)

    member_tasks = [
        task for task in tasks
        if task.get("assigned_to", "").lower() == username.lower()
    ]

    total = len(member_tasks)

    completed = sum(
        1 for task in member_tasks
        if task.get("status") == "Completed"
    )

    in_progress = sum(
        1 for task in member_tasks
        if task.get("status") == "In Progress"
    )

    overdue = sum(
        1 for task in member_tasks
        if task.get("status") != "Completed"
        and task.get("due_date")
        and task["due_date"] < date.today().isoformat()
    )

    return {
        "username": username,
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "overdue": overdue
    }


def get_all_member_reports():
    """Return reports for all registered members."""

    users = load_data(USERS_FILE)

    return [
        get_member_report(user["username"])
        for user in users
        if user.get("role") == "member"
    ]


def get_overdue_tasks():
    """Return all overdue tasks."""

    tasks = load_data(TASKS_FILE)
    today = date.today().isoformat()

    return [
        task for task in tasks
        if task.get("status") != "Completed"
        and task.get("due_date")
        and task["due_date"] < today
    ]
