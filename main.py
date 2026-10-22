from utils import console, print_header, prompt_select, show_spinner
from storage import load_data, save_data
from services.subject_service import manage_subjects_menu
from services.task_service import manage_tasks_menu
from services.dashboard_service import show_dashboard
from models.classes import Subject, Task, Exam, StudyNote


def hydrate_data(raw_data):
    """Convert raw JSON dictionaries into rich model objects."""
    subjects = [Subject(**s) for s in raw_data.get("subjects", [])]
    tasks = [Task(**t) for t in raw_data.get("tasks", [])]
    exams = [Exam(**e) for e in raw_data.get("exams", [])]
    notes = [StudyNote(**n) for n in raw_data.get("notes", [])]
    return {"subjects": subjects, "tasks": tasks, "exams": exams, "notes": notes}


def main():
    show_spinner("Starting StudyMate Academic Assistant...")
    
    # Load data from JSON storage
    raw_data = load_data()
    data = hydrate_data(raw_data)

    while True:
        print_header(
            "StudyMate — Smart University Academic Assistant",
            "Main Menu: Choose a section below using Up/Down arrow keys and press Enter"
        )

        choices = [
            "1. Academic Progress & Grades Dashboard",
            "2. Manage Subjects",
            "3. Manage Tasks & Assignments",
            "4. Manage Exams",
            "5. Manage Study Notes",
            "6. Save and Exit"
        ]

        choice = prompt_select("Select a section to open:", choices)

        if choice is None or "6." in choice:
            show_spinner("Saving your academic records...")
            final_data = {
                "subjects": [s.to_dict() for s in data["subjects"]],
                "tasks": [t.to_dict() for t in data["tasks"]],
                "exams": [e.to_dict() for e in data["exams"]],
                "notes": [n.to_dict() for n in data["notes"]]
            }
            save_data(final_data)
            console.print("\n[bold cyan]All data saved in StudyMate. Goodbye![/bold cyan]\n")
            break
        elif "1." in choice:
            show_dashboard(data)
        elif "2." in choice:
            manage_subjects_menu(data)
        elif "3." in choice:
            manage_tasks_menu(data)
        elif "4." in choice:
            console.print("[yellow]-> Exams section (Coming soon!)[/yellow]")
        elif "5." in choice:
            console.print("[yellow]-> Study Notes section (Coming soon!)[/yellow]")


if __name__ == "__main__":
    main()