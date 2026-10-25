import time
import uuid
from datetime import datetime
from functools import wraps
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich import box
from models.classes import StudyNote
from storage import save_data
from utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_select,
    prompt_required_text
)


# --- 1. Custom Exception Class ---
class TimerInterruptedError(Exception):
    """Custom exception raised when a student stops the study timer early."""
    pass


# --- 2. Decorator (@log_activity) ---
def log_activity(action_name):
    """Decorator that logs user actions with timestamps to activity.log."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("activity.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[{timestamp}] STARTED: {action_name}\n")
            result = func(*args, **kwargs)
            with open("activity.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[{timestamp}] COMPLETED: {action_name}\n")
            return result
        return wrapper
    return decorator


# --- 3. Inheritance (Base Class & Child Class) ---
class BaseTimer:
    """Parent class representing a basic countdown timer."""
    def __init__(self, duration_minutes):
        self.duration_minutes = duration_minutes
        self.total_seconds = int(duration_minutes * 60)

    def get_session_label(self):
        return f"{self.duration_minutes} min timer"


class StudyTimerSession(BaseTimer):
    """Child class inheriting from BaseTimer for course study sessions."""
    def __init__(self, subject_code, subject_name, duration_minutes):
        super().__init__(duration_minutes)
        self.subject_code = subject_code
        self.subject_name = subject_name

    def get_session_label(self):
        return f"Study Timer: {self.subject_code} ({self.subject_name}) — {self.duration_minutes} mins"


# --- 4. Study Timer Logic & Menu ---
@log_activity("Study Timer Session")
def start_study_timer(data, subject, duration_mins, is_demo=False):
    session = StudyTimerSession(subject.code, subject.name, duration_mins)
    total_secs = 10 if is_demo else session.total_seconds

    # Using lambda + filter to count previous study sessions for this subject
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
            task = progress.add_task(f"Studying {subject.code}...", total=total_secs)
            for _ in range(total_secs):
                time.sleep(1)
                progress.update(task, advance=1)

        # Auto-save a StudyNote upon completion
        new_note = StudyNote(
            note_id=str(uuid.uuid4())[:8],
            title=f"Study Session ({duration_mins} mins)",
            content=f"Completed a {duration_mins}-minute study session for {subject.code} ({subject.name}).",
            subject_id=subject.subject_id
        )
        data["notes"].append(new_note)
        save_data(data)

        print_success(f"Session completed! ({duration_mins} mins logged to your Study Notes).")

    except KeyboardInterrupt:
        try:
            raise TimerInterruptedError("Study timer was stopped early.")
        except TimerInterruptedError as err:
            console.print()
            print_error(f"{err} Session was not saved.")


def manage_pomodoro_menu(data):
    while True:
        print_header(
            "Study Timer",
            "Track your study time for each course"
        )
        subjects = data.get("subjects", [])
        if not subjects:
            print_info("No subjects available. Please add a subject first.")
            return

        choices = [
            "1. Quick Demo (10 Seconds)",
            "2. Standard Timer (25 Minutes)",
            "3. Custom Timer Duration",
            "4. View Activity Log",
            "5. Back to Main Menu"
        ]
        choice = prompt_select("Study Timer Menu:", choices)

        if not choice or "5." in choice:
            break
        elif "4." in choice:
            try:
                with open("activity.log", "r", encoding="utf-8") as f:
                    logs = f.read().strip()
                console.print(Panel(logs if logs else "No activity recorded yet.", title="[bold cyan]Activity Log[/bold cyan]", border_style="cyan"))
            except FileNotFoundError:
                print_info("No activity log found yet. Start a timer first!")
            continue

        sub_choices = [f"{s.code} - {s.name}" for s in subjects]
        sub_choice = prompt_select("Select Subject:", sub_choices)
        if not sub_choice:
            continue
        selected_sub = subjects[sub_choices.index(sub_choice)]

        if "1." in choice:
            start_study_timer(data, selected_sub, duration_mins=25, is_demo=True)
        elif "2." in choice:
            start_study_timer(data, selected_sub, duration_mins=25, is_demo=False)
        elif "3." in choice:
            raw_mins = prompt_required_text("Enter timer duration in minutes (1 - 180):", default_value="25")
            try:
                mins = max(1, min(180, int(raw_mins)))
            except ValueError:
                mins = 25
            start_study_timer(data, selected_sub, duration_mins=mins, is_demo=False)