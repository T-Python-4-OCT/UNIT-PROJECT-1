from utils import console, print_header, prompt_select, show_spinner
from storage import load_data, save_data
from services.auth_service import auth_menu
from services.dashboard_service import show_dashboard
from services.subject_service import manage_subjects_menu
from services.task_service import manage_tasks_menu
from services.project_service import manage_projects_menu
from services.exam_service import manage_exams_menu
from services.note_service import manage_notes_menu
from models.classes import User, Subject, Task, Project, Exam, StudyNote

def hydrate_data(raw_data):
    users = [User(**u) for u in raw_data.get("users", [])]
    subjects = [Subject(**s) for s in raw_data.get("subjects", [])]
    tasks = [Task(**t) for t in raw_data.get("tasks", [])]
    projects = [Project(**p) for p in raw_data.get("projects", [])]
    exams = [Exam(**e) for e in raw_data.get("exams", [])]
    notes = [StudyNote(**n) for n in raw_data.get("notes", [])]
    return {
        "users": users,
        "subjects": subjects,
        "tasks": tasks,
        "projects": projects,
        "exams": exams,
        "notes": notes
    }

def main():
    show_spinner("Starting StudyMate Academic Assistant...")
    raw_data = load_data()
    data = hydrate_data(raw_data)

    while True:
        # شاشة تسجيل الدخول
        current_user = auth_menu(data)
        if not current_user:
            console.print("\n[bold cyan]Goodbye![/bold cyan]\n")
            break

        # القائمة الرئيسية بعد تسجيل الدخول بنجاح
        while True:
            print_header(
                "StudyMate — Smart University Academic Assistant",
                f"👤 Logged in as: {current_user.full_name} ({current_user.username}) | 🎓 Major: {current_user.major}"
            )

            choices = [
                "1. Academic Progress & Grades Dashboard",
                "2. Manage Subjects",
                "3. Manage Tasks & Assignments",
                "4. Manage Academic Projects",
                "5. Manage Exams",
                "6. Manage Study Notes",
                "7. Logout (Switch Account)",
                "8. Save and Exit"
            ]

            choice = prompt_select("Main Menu:", choices)

            if choice is None or "8." in choice:
                show_spinner("Saving your academic records...")
                save_data(data)
                console.print(f"\n[bold cyan]All data saved. Goodbye, {current_user.full_name}![/bold cyan]\n")
                return
            elif "7." in choice:
                show_spinner("Logging out...")
                save_data(data)
                break
            elif "1." in choice:
                show_dashboard(data)
            elif "2." in choice:
                manage_subjects_menu(data)
            elif "3." in choice:
                manage_tasks_menu(data)
            elif "4." in choice:
                manage_projects_menu(data)
            elif "5." in choice:
                manage_exams_menu(data)
            elif "6." in choice:
                manage_notes_menu(data)

if __name__ == "__main__":
    main()