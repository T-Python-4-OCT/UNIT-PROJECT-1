"""Data model classes for the StudyMate application."""

from datetime import datetime, date

VALID_PRIORITIES = ["High", "Medium", "Low"]
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]
VALID_EXAM_TYPES = ["Quiz", "Midterm", "Final"]


class Subject:
    def __init__(self, subject_id, name, code, instructor, credit_hours):
        self.subject_id = str(subject_id).strip()
        self.name = str(name).strip()
        self.code = str(code).strip().upper()
        self.instructor = str(instructor).strip()
        self.credit_hours = int(credit_hours)

    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "code": self.code,
            "instructor": self.instructor,
            "credit_hours": self.credit_hours
        }


class Task:
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
        self.task_id = str(task_id).strip()
        self.title = str(title).strip()
        self.description = str(description).strip()
        self.subject_id = str(subject_id).strip()
        self.due_date = str(due_date).strip()
        self.priority = priority
        self.status = status

        if earned_score is not None and str(earned_score).strip() != "":
            self.earned_score = float(earned_score)
        else:
            self.earned_score = None

        if max_score is not None and str(max_score).strip() != "":
            self.max_score = float(max_score)
        else:
            self.max_score = None

        if created_at is None or str(created_at).strip() == "":
            self.created_at = date.today().strftime("%Y-%m-%d")
        else:
            self.created_at = str(created_at).strip()

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


class Exam:
    def __init__(
        self,
        exam_id,
        title,
        subject_id,
        exam_date,
        exam_time,
        exam_type="Midterm",
        earned_score=None,
        max_score=100.0
    ):
        self.exam_id = str(exam_id).strip()
        self.title = str(title).strip()
        self.subject_id = str(subject_id).strip()
        self.exam_date = str(exam_date).strip()
        self.exam_time = str(exam_time).strip()
        self.exam_type = exam_type

        if earned_score is not None and str(earned_score).strip() != "":
            self.earned_score = float(earned_score)
        else:
            self.earned_score = None

        if max_score is not None and str(max_score).strip() != "":
            self.max_score = float(max_score)
        else:
            self.max_score = 100.0

    def get_exam_date_object(self):
        return datetime.strptime(self.exam_date, "%Y-%m-%d").date()

    def is_upcoming(self):
        return self.get_exam_date_object() >= date.today()

    def days_until_exam(self):
        return (self.get_exam_date_object() - date.today()).days

    def to_dict(self):
        return {
            "exam_id": self.exam_id,
            "title": self.title,
            "subject_id": self.subject_id,
            "exam_date": self.exam_date,
            "exam_time": self.exam_time,
            "exam_type": self.exam_type,
            "earned_score": self.earned_score,
            "max_score": self.max_score
        }


class StudyNote:
    def __init__(self, note_id, title, content, subject_id=None, created_at=None):
        self.note_id = str(note_id).strip()
        self.title = str(title).strip()
        self.content = str(content).strip()

        if subject_id is not None and str(subject_id).strip() != "":
            self.subject_id = str(subject_id).strip()
        else:
            self.subject_id = None

        if created_at is None or str(created_at).strip() == "":
            self.created_at = date.today().strftime("%Y-%m-%d")
        else:
            self.created_at = str(created_at).strip()

    def to_dict(self):
        return {
            "note_id": self.note_id,
            "title": self.title,
            "content": self.content,
            "subject_id": self.subject_id,
            "created_at": self.created_at
        }


def create_subject_from_dict(d):
    return Subject(
        d.get("subject_id"),
        d.get("name"),
        d.get("code"),
        d.get("instructor"),
        d.get("credit_hours", 3)
    )


def create_task_from_dict(d):
    return Task(
        d.get("task_id"),
        d.get("title"),
        d.get("description", ""),
        d.get("subject_id"),
        d.get("due_date"),
        d.get("priority", "Medium"),
        d.get("status", "Not Started"),
        d.get("earned_score", None),
        d.get("max_score", None),
        d.get("created_at", None)
    )


def create_exam_from_dict(d):
    return Exam(
        d.get("exam_id"),
        d.get("title"),
        d.get("subject_id"),
        d.get("exam_date"),
        d.get("exam_time"),
        d.get("exam_type", "Midterm"),
        d.get("earned_score", None),
        d.get("max_score", 100.0)
    )


def create_note_from_dict(d):
    return StudyNote(
        d.get("note_id"),
        d.get("title"),
        d.get("content"),
        d.get("subject_id"),
        d.get("created_at")
    )