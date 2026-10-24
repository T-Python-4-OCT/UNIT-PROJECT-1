from rich.table import Table
from rich.panel import Panel
from models.classes import StudyNote
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_required_text,
    prompt_select,
    confirm_delete,
    show_spinner
)

def manage_notes_menu(data):
    while True:
        print_header(
            "SECTION: Study Notes Management",
            "Create, read, or delete your lecture notes"
        )
        choices = [
            "1. View All Notes",
            "2. Read Note Content",
            "3. Add New Note",
            "4. Delete Note",
            "5. Back to Main Menu"
        ]
        choice = prompt_select("Select an action:", choices)

        if choice is None or "5." in choice:
            break
        elif "1." in choice:
            view_all_notes(data)
        elif "2." in choice:
            read_note(data)
        elif "3." in choice:
            add_note(data)
        elif "4." in choice:
            delete_note(data)

def view_all_notes(data):
    print_header("VIEW: All Study Notes", "List of saved study summaries")
    show_spinner("Loading notes...")
    notes = data["notes"]

    if not notes:
        print_info("No study notes found.")
        return

    sub_map = {s.subject_id: s.code for s in data["subjects"]}

    table = Table(title=f"Study Notes (Total: {len(notes)})", show_header=True, header_style="bold cyan")
    table.add_column("Note ID", width=10)
    table.add_column("Title", width=30)
    table.add_column("Course", width=12)
    table.add_column("Created At", width=14)

    for n in notes:
        course_code = sub_map.get(n.subject_id, "General")
        table.add_row(n.note_id, n.title, f"[bold]{course_code}[/bold]", n.created_at)

    console.print()
    console.print(table)

def read_note(data):
    if not data["notes"]:
        print_info("No notes available to read.")
        return

    choices = [f"[{n.note_id}] {n.title}" for n in data["notes"]]
    choices.append("Cancel")

    selected = prompt_select("Select a note to read:", choices)
    if not selected or selected == "Cancel":
        return

    note_id = selected.split("]")[0].replace("[", "").strip()
    target_note = next((n for n in data["notes"] if n.note_id == note_id), None)

    if target_note:
        console.print()
        console.print(Panel(target_note.content, title=f"[bold cyan]{target_note.title}[/bold cyan] ({target_note.created_at})", border_style="cyan"))

def generate_next_note_id(notes):
    max_num = 0
    for n in notes:
        if n.note_id.startswith("NTE-"):
            num_part = n.note_id.replace("NTE-", "")
            if num_part.isdigit():
                num = int(num_part)
                if num > max_num:
                    max_num = num
    return f"NTE-{max_num + 1:03d}"

def add_note(data):
    print_header("ACTION: Add New Study Note", "Write a new study summary")
    if not data["subjects"]:
        print_error("Please add a subject first.")
        return

    sub_choices = [f"[{s.subject_id}] {s.code} - {s.name}" for s in data["subjects"]]
    selected_sub = prompt_select("Select Course:", sub_choices)
    if not selected_sub:
        return

    sub_id = selected_sub.split("]")[0].replace("[", "").strip()
    title = prompt_required_text("Enter Note Title:")
    content = prompt_required_text("Enter Note Content:")

    new_id = generate_next_note_id(data["notes"])
    new_note = StudyNote(new_id, title, content, sub_id)

    show_spinner("Saving note...")
    data["notes"].append(new_note)
    save_data(data)
    print_success(f"Note '{title}' added successfully.")

def delete_note(data):
    print_header("ACTION: Delete Note", "Remove a study note")
    if not data["notes"]:
        print_info("No notes available.")
        return

    choices = [f"[{n.note_id}] {n.title}" for n in data["notes"]]
    choices.append("Cancel")

    selected = prompt_select("Select note to delete:", choices)
    if not selected or selected == "Cancel":
        return

    note_id = selected.split("]")[0].replace("[", "").strip()
    if confirm_delete(selected):
        data["notes"] = [n for n in data["notes"] if n.note_id != note_id]
        save_data(data)
        print_success("Note deleted successfully.")
    else:
        print_info("Deletion cancelled.")