"""
services/pomodoro_service.py
Study timer that logs completed sessions to study notes and activity.log.
"""
import time
from datetime import datetime
from functools import wraps
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich import box
from models.classes import StudyNote
from storage import save_data
from services.base_service import BaseService, generate_next_id
from utils import (
    console,
    print_success,
    print_error,
    print_info,
    prompt_int_range
)


# Custom exception when the timer is stopped early
class TimerInterruptedError(Exception):
    pass


# Decorator to log timer start and end times in activity.log
def log_activity(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("activity.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[{started}] STARTED: {action_name}\n")
            result = func(*args, **kwargs)
            finished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("activity.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[{finished}] COMPLETED: {action_name}\n")
            return result
        return wrapper
    return decorator


# Timer classes
class BaseTimer:
    def __init__(self, duration_minutes):
        self.duration_minutes = duration_minutes
        self.total_seconds = int(duration_minutes * 60)

    def get_session_label(self):
        return f"{self.duration_minutes} min timer"


class StudyTimerSession(BaseTimer):
    def __init__(self, subject_code, subject_name, duration_minutes):
        super().__init__(duration_minutes)
        self.subject_code = subject_code
        self.subject_name = subject_name

    def get_session_label(self):
        return f"Study Timer: {self.subject_code} ({self.subject_name}) — {self.duration_minutes} mins"


@log_activity("Study Timer Session")
def start_study_timer(data, subject, duration_mins, is_demo=False):
    session = StudyTimerSession(subject.code, subject.name, duration_mins)
    total_secs = 10 if is_demo else session.total_seconds

    # Count previous study sessions for this course
    notes = data.get("notes", [])
    prev_sessions = list(filter(
        lambda n: n.subject_id == subject.subject_id and "Study Session" in n.title,
        notes
    ))

    console.print()
    console.print(Panel(
        f"[bold cyan]{session.get_session_label()}[/bold cyan]\n"
        f"[white]Completed Sessions for {subject.code}:[/white] [bold green]{len(prev_sessions)}[/bold green]\n"
        f"[dim]Press Ctrl+C at any time to stop the timer.[/dim]",
        title="[bold yellow]⏱️ Study Timer[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED
    ))
    console.print()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"📚 Studying {subject.code}...", total=total_secs)
            for _ in range(total_secs):
                time.sleep(1)
                progress.update(task, advance=1)

        # Save a note automatically when the timer finishes
        new_note = StudyNote(
            note_id=generate_next_id(notes, "NTE", "note_id"),
            title=f"Study Session ({duration_mins} mins)",
            content=f"Completed a {duration_mins}-minute study session for {subject.code} ({subject.name}).",
            subject_id=subject.subject_id
        )
        data["notes"].append(new_note)
        save_data(data)

        print_success(f"🎉 Session completed! ({duration_mins} mins saved to your Study Notes).")

    except KeyboardInterrupt:
        try:
            raise TimerInterruptedError("Study timer was stopped early.")
        except TimerInterruptedError as err:
            console.print()
            print_error(f"{err} Session was not saved.")


class PomodoroService(BaseService):
    section_title = "⏱️  Study Timer"
    section_subtitle = "Track your study time for each course"
    menu_prompt = "Study Timer Menu:"
    menu_options = [
        ("⚡ Quick Demo (10 Seconds)", "demo"),
        ("🍅 Standard Timer (25 Minutes)", "standard"),
        ("🎚️  Custom Timer Duration", "custom"),
        ("📜 View Activity Log", "view_log"),
    ]

    def can_open(self):
        if not self.data.get("subjects"):
            print_info("No subjects available. Please add a subject first.")
            return False
        return True

    def demo(self):
        subject = self.select_subject("Select Subject:")
        if subject:
            start_study_timer(self.data, subject, duration_mins=25, is_demo=True)

    def standard(self):
        subject = self.select_subject("Select Subject:")
        if subject:
            start_study_timer(self.data, subject, duration_mins=25, is_demo=False)

    def custom(self):
        subject = self.select_subject("Select Subject:")
        if not subject:
            return
        mins = prompt_int_range("⏳ Timer duration in minutes (1 - 180):", 1, 180, 25)
        start_study_timer(self.data, subject, duration_mins=mins, is_demo=False)

    def view_log(self):
        try:
            with open("activity.log", "r", encoding="utf-8") as f:
                logs = f.read().strip()
            console.print(Panel(logs if logs else "No activity recorded yet.",
                                title="[bold cyan]📜 Activity Log[/bold cyan]", border_style="cyan"))
        except FileNotFoundError:
            print_info("No activity log found yet. Start a timer first!")


def manage_pomodoro_menu(data):
    PomodoroService(data).run()