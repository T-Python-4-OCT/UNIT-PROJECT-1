"""
services/note_service.py
Create, read, and delete study notes.
"""
from rich.table import Table
from rich.panel import Panel
from models.classes import StudyNote
from services.base_service import BaseService
from utils import (
    console,
    print_header,
    print_success,
    print_info,
    prompt_text,
    show_spinner
)


class NoteService(BaseService):
    section_title = "🗒️  Manage Study Notes"
    section_subtitle = "Create, read, or delete your lecture notes"
    menu_options = [
        ("📋 View All Notes", "view_all"),
        ("📖 Read Note Content", "read"),
        ("➕ Add New Note", "add"),
        ("🗑️  Delete Note", "delete"),
    ]

    def view_all(self):
        print_header("📋 All Study Notes", "List of saved study notes")
        show_spinner("Loading notes...")
        notes = self.data["notes"]

        if not notes:
            print_info("No study notes found.")
            return

        sub_map = {s.subject_id: s.code for s in self.data["subjects"]}

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

    def read(self):
        if not self.data["notes"]:
            print_info("No notes available to read.")
            return

        note = self.select_item(self.data["notes"], lambda n: f"[{n.note_id}] {n.title}", "Select a note to read:")
        if note:
            console.print()
            console.print(Panel(
                note.content,
                title=f"[bold cyan]📖 {note.title}[/bold cyan] ({note.created_at})",
                border_style="cyan"
            ))

    def add(self):
        print_header("➕ Add New Study Note", "Write a new study note")

        subject = self.select_subject()
        if not subject:
            return

        title = prompt_text("📝 Note Title:")
        content = prompt_text("✍️  Note Content:")

        new_note = StudyNote(self.next_id("notes", "NTE", "note_id"), title, content, subject.subject_id)

        show_spinner("Saving note...")
        self.data["notes"].append(new_note)
        self.save()
        print_success(f"Note '{title}' added successfully.")

    def delete(self):
        print_header("🗑️  Delete Note", "Remove a study note")
        self.delete_record("notes", lambda n: f"[{n.note_id}] {n.title}", "note")


def manage_notes_menu(data):
    NoteService(data).run()