"""
main.py
Main entry point for UniMate.
"""
from utils import console, print_header, print_info, prompt_select, show_spinner, InputCancelled
from storage import load_data, save_data
from services.auth_service import auth_menu
from services.dashboard_service import show_dashboard
from services.subject_service import manage_subjects_menu
from services.task_service import manage_tasks_menu
from services.project_service import manage_projects_menu
from services.exam_service import manage_exams_menu
from services.note_service import manage_notes_menu
from services.pomodoro_service import manage_pomodoro_menu
from models.classes import User, Subject, Task, Project, Exam, StudyNote


def hydrate_data(raw_data):
    # Convert dictionaries from JSON into class objects
    return {
        "users": [User(**u) for u in raw_data.get("users", [])],
        "subjects": [Subject(**s) for s in raw_data.get("subjects", [])],
        "tasks": [Task(**t) for t in raw_data.get("tasks", [])],
        "projects": [Project(**p) for p in raw_data.get("projects", [])],
        "exams": [Exam(**e) for e in raw_data.get("exams", [])],
        "notes": [StudyNote(**n) for n in raw_data.get("notes", [])]
    }


MENU_ITEMS = [
    ("📊 Academic Progress & Grades Dashboard", show_dashboard),
    ("📚 Manage Subjects", manage_subjects_menu),
    ("📝 Manage Tasks & Assignments", manage_tasks_menu),
    ("🚀 Manage Academic Projects", manage_projects_menu),
    ("🎓 Manage Exams", manage_exams_menu),
    ("🗒️  Manage Study Notes", manage_notes_menu),
    ("⏱️  Study Timer", manage_pomodoro_menu),
]


def main():
    show_spinner("Starting UniMate...")
    data = hydrate_data(load_data())

    current_user = auth_menu(data)
    if not current_user:
        console.print("\n[bold cyan]👋 Goodbye![/bold cyan]\n")
        return

    choices = [f"{i}. {label}" for i, (label, _) in enumerate(MENU_ITEMS, 1)]
    choices.append(f"{len(MENU_ITEMS) + 1}. 💾 Save and Exit")

    while True:
        print_header(
            "🎓 UniMate — University Academic Assistant",
            f"👤 User: {current_user.full_name} ({current_user.username}) | 🎓 Major: {current_user.major}"
        )

        choice = prompt_select("Main Menu:", choices)

        if choice is None or choices.index(choice) == len(MENU_ITEMS):
            show_spinner("Saving your data...")
            save_data(data)
            console.print(f"\n[bold cyan]💾 All data saved. Goodbye, {current_user.full_name}! 👋[/bold cyan]\n")
            break

        handler = MENU_ITEMS[choices.index(choice)][1]
        try:
            handler(data)
        except InputCancelled:
            print_info("Action cancelled. Returning to main menu.")


if __name__ == "__main__":
    main()