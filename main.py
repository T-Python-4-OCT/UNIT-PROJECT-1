from utils import console, print_header, prompt_select, show_spinner
from storage import load_data, save_data
from services.dashboard_service import show_dashboard
from services.subject_service import manage_subjects_menu
from services.task_service import manage_tasks_menu
from services.exam_service import manage_exams_menu
from services.note_service import manage_notes_menu
from models.classes import Subject, Task, Exam, StudyNote

def hydrate_data(raw_data):
    subjects = [Subject(**s) for s in raw_data.get("subjects", [])]
    tasks = [Task(**t) for t in raw_data.get("tasks", [])]
    exams = [Exam(**e) for e in raw_data.get("exams", [])]
    notes = [StudyNote(**n) for n in raw_data.get("notes", [])]
    return {"subjects": subjects, "tasks": tasks, "exams": exams, "notes": notes}

def main():
    show_spinner("Starting StudyMate Academic Assistant...")
    raw_data = load_data()
    data = hydrate_data(raw_data)

    while True:
        print_header(
            "StudyMate — Smart University Academic Assistant",
            "Use Up/Down arrow keys to navigate and press Enter to select"
        )

        choices = [
            "1. Academic Progress & Grades Dashboard",
            "2. Manage Subjects",
            "3. Manage Tasks & Assignments",
            "4. Manage Exams",
            "5. Manage Study Notes",
            "6. Save and Exit"
        ]

        choice = prompt_select("Main Menu:", choices)

        if choice is None or "6." in choice:
            show_spinner("Saving your academic records...")
            save_data(data)
            console.print("\n[bold cyan]All data saved in StudyMate. Goodbye![/bold cyan]\n")
            break
        elif "1." in choice:
            show_dashboard(data)
        elif "2." in choice:
            manage_subjects_menu(data)
        elif "3." in choice:
            manage_tasks_menu(data)
        elif "4." in choice:
            manage_exams_menu(data)
        elif "5." in choice:
            manage_notes_menu(data)

if __name__ == "__main__":
    main()