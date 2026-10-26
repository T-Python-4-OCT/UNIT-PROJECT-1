"""
services/pomodoro_service.py
Study and break timers with live keyboard controls (Pause, Resume, Break, Cancel).
"""
import time
from datetime import datetime
from functools import wraps

# Built-in Windows module to read key presses while the timer is running
try:
    import msvcrt
except ImportError:
    msvcrt = None

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
    prompt_int_range,
    prompt_select
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


class BreakTimerSession(BaseTimer):
    def __init__(self, duration_minutes):
        super().__init__(duration_minutes)

    def get_session_label(self):
        return f"Break Timer — {self.duration_minutes} mins (Relax & Recharge)"


def _clear_key_buffer():
    # Clear any extra pressed keys before returning to the menu
    if msvcrt:
        while msvcrt.kbhit():
            msvcrt.getwch()


def _read_key():
    # Read a single key press without stopping the timer
    if msvcrt and msvcrt.kbhit():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            if msvcrt.kbhit():
                msvcrt.getwch()
            return None
        return ch.lower()
    return None


def run_live_countdown(total_secs, active_label, bar_color="green", text_color="cyan", allow_break_switch=False):
    """
    Run the countdown bar with live keyboard shortcuts:
      [P] Pause / Resume
      [B] Switch to Break (when studying)
      [Q] Cancel & Back to Menu
    Returns "completed" or "switch_to_break".
    """
    _clear_key_buffer()
    paused = False

    with Progress(
        SpinnerColumn(style=bar_color),
        TextColumn("{task.description}"),
        BarColumn(bar_width=38, complete_style=bar_color, finished_style=f"bold {bar_color}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[bold {text_color}]{active_label}[/bold {text_color}]", total=total_secs)
        elapsed_tenths = 0
        total_tenths = total_secs * 10

        while elapsed_tenths < total_tenths:
            key = _read_key()

            if key == "p":
                paused = not paused
                if paused:
                    progress.update(
                        task,
                        description="[bold yellow]⏸️  PAUSED — Press [P] Resume | [Q] Cancel[/bold yellow]"
                    )
                else:
                    progress.update(
                        task,
                        description=f"[bold {text_color}]{active_label}[/bold {text_color}]"
                    )
            elif key in ("q", "c"):
                _clear_key_buffer()
                raise TimerInterruptedError("Timer cancelled. Returning to menu.")
            elif key == "b" and allow_break_switch:
                _clear_key_buffer()
                return "switch_to_break"

            time.sleep(0.1)

            if not paused:
                elapsed_tenths += 1
                if elapsed_tenths % 10 == 0:
                    progress.update(task, advance=1)

    _clear_key_buffer()
    return "completed"


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
        f"[white]Completed Sessions for {subject.code}:[/white] [bold green]{len(prev_sessions)}[/bold green]\n\n"
        f"[bold yellow]Live Controls:[/bold yellow]  "
        f"[bold white][P][/bold white] Pause / Resume   |   "
        f"[bold magenta][B][/bold magenta] Start Break   |   "
        f"[bold red][Q][/bold red] Cancel & Back to Menu",
        title="[bold yellow]⏱️ Study Timer[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED
    ))
    console.print()

    try:
        status = run_live_countdown(
            total_secs=total_secs,
            active_label=f"📚 Studying {subject.code}...",
            bar_color="green",
            text_color="cyan",
            allow_break_switch=True
        )

        # If the user pressed [B], switch directly to the break timer
        if status == "switch_to_break":
            print_info("Switching to Break Timer...")
            start_break_timer(duration_mins=5, is_demo=is_demo)
            return

        # Save a study note automatically when the timer finishes
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
        console.print()
        print_error("Timer cancelled. Session was not saved.")
    except TimerInterruptedError as err:
        console.print()
        print_error(f"{err} Session was not saved.")


@log_activity("Break Timer Session")
def start_break_timer(duration_mins, is_demo=False):
    session = BreakTimerSession(duration_mins)
    total_secs = 10 if is_demo else session.total_seconds

    # Break timer uses a magenta color theme so it looks distinct from the study timer
    console.print()
    console.print(Panel(
        f"[bold magenta]{session.get_session_label()}[/bold magenta]\n"
        f"[white]Take a rest and step away from your screen![/white]\n\n"
        f"[bold magenta]Live Controls:[/bold magenta]  "
        f"[bold white][P][/bold white] Pause / Resume   |   "
        f"[bold red][Q][/bold red] Cancel & Back to Menu",
        title="[bold magenta]☕ Break Timer[/bold magenta]",
        border_style="magenta",
        box=box.ROUNDED
    ))
    console.print()

    try:
        run_live_countdown(
            total_secs=total_secs,
            active_label="☕ On Break...",
            bar_color="magenta",
            text_color="magenta",
            allow_break_switch=False
        )
        print_success(f"🔔 Break finished! ({duration_mins} mins). Ready to study again!")

    except KeyboardInterrupt:
        console.print()
        print_info("Break cancelled. Returning to menu.")
    except TimerInterruptedError as err:
        console.print()
        print_info(str(err))


class PomodoroService(BaseService):
    section_title = "⏱️  Study & Break Timer"
    section_subtitle = "Track your study time and breaks for each course"
    menu_prompt = "Timer Menu:"
    menu_options = [
        ("⚡ Quick Study Demo (10 Seconds)", "demo"),
        ("🍅 Standard Study Timer (25 Minutes)", "standard"),
        ("🎚️  Custom Study Timer", "custom"),
        ("☕ Start Break Timer", "break_menu"),
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
        mins = prompt_int_range("⏳ Study duration in minutes (1 - 180):", 1, 180, 25)
        start_study_timer(self.data, subject, duration_mins=mins, is_demo=False)

    def break_menu(self):
        choice = prompt_select(
            "Select Break Duration:",
            [
                "1. ⚡ Quick Break Demo (10 Seconds)",
                "2. ☕ Short Break (5 Minutes)",
                "3. 🛋️  Long Break (15 Minutes)",
                "4. 🎚️  Custom Break Duration",
                "5. 🔙 Back"
            ]
        )
        if not choice or "5." in choice:
            return

        if "1." in choice:
            start_break_timer(duration_mins=5, is_demo=True)
        elif "2." in choice:
            start_break_timer(duration_mins=5, is_demo=False)
        elif "3." in choice:
            start_break_timer(duration_mins=15, is_demo=False)
        elif "4." in choice:
            mins = prompt_int_range("☕ Break duration in minutes (1 - 60):", 1, 60, 10)
            start_break_timer(duration_mins=mins, is_demo=False)

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