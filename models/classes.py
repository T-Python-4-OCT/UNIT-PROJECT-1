"""Data model classes for the StudyMate application."""

from datetime import datetime, date

VALID_PRIORITIES = ["High", "Medium", "Low"]
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]
VALID_EXAM_TYPES = ["Quiz", "Midterm", "Final"]


class Subject:
    """Represents a university course or academic subject."""

    def __init__(self, subject_id, name, code, instructor, credit_hours):
        if not str(subject_id).strip():
            raise ValueError("Subject ID cannot be empty.")
        if not str(name).strip():
            raise ValueError("Subject name cannot be empty.")
        if not str(code).strip():
            raise ValueError("Course code cannot be empty.")
        if not str(instructor).strip():
            raise ValueError("Instructor name cannot be empty.")

        try:
            hours = int(credit_hours)
        except (ValueError, TypeError):
            raise ValueError("Credit hours must be a whole number.")

        if hours <= 0:
            raise ValueError("Credit hours must be a positive number.")

        self.subject_id = str(subject_id).strip()
        self.name = str(name).strip()
        self.code = str(code).strip().upper()
        self.instructor = str(instructor).strip()
        self.credit_hours = hours

    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "code": self.code,
            "instructor": self.instructor,
            "credit_hours": self.credit_hours
        }


class Task:
    """Represents an academic assignment or project with optional grading."""

    def __init__(
        self,
        task_id,
        title,
        description,
        subject_id,
        due_date,
        priority="Medium",
        status="Not Started",
        earned_score=None,
        max_score=None,
        created_at=None
    ):
        if not str(task_id).strip():
            raise ValueError("Task ID cannot be empty.")
        if not str(title).strip():
            raise ValueError("Task title cannot be empty.")
        if not str(subject_id).strip():
            raise ValueError("Subject ID cannot be empty.")

        try:
            datetime.strptime(str(due_date).strip(), "%Y-%m-%d")
        except ValueError:
            raise ValueError("Due date must be in YYYY-MM-DD format.")

        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}.")

        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}.")

        parsed_earned = float(earned_score) if earned_score is not None and str(earned_score).strip() != "" else None
        parsed_max = float(max_score) if max_score is not None and str(max_score).strip() != "" else None

        if created_at is None or not str(created_at).strip():
            created_at_str = date.today().strftime("%Y-%m-%d")
        else:
            created_at_str = str(created_at).strip()

        self.task_id = str(task_id).strip()
        self.title = str(title).strip()
        self.description = str(description).strip()
        self.subject_id = str(subject_id).strip()
        self.due_date = str(due_date).strip()
        self.priority = priority
        self.status = status
        self.earned_score = parsed_earned
        self.max_score = parsed_max
        self.created_at = created_at_str

    def get_due_date_object(self):
        return datetime.strptime(self.due_date, "%Y-%m-%d").date()

    def is_overdue(self):
        if self.status == "Completed":
            return False
        return self.get_due_date_object() < date.today()

    def days_until_due(self):
        return (self.get_due_date_object() - date.today()).days

    def mark_completed(self, earned=None, max_s=None):
        self.status = "Completed"
        if earned is not None:
            self.earned_score = float(earned)
        if max_s is not None:
            self.max_score = float(max_s)

    def reopen(self):
        self.status = "In Progress"

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "subject_id": self.subject_id,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "earned_score": self.earned_score,
            "max_score": self.max_score,
            "created_at": self.created_at
        }

