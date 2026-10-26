"""
models/classes.py
Main classes used in UniMate.
"""
from datetime import datetime, date
import hashlib


# Base class for items that have grades (Task, Project, Exam)
class ScoredItem:
    def __init__(self, earned_score=None, max_score=None):
        self._earned_score = None
        self._max_score = None

        if earned_score is not None:
            self.set_earned_score(earned_score)
        if max_score is not None:
            self.set_max_score(max_score)

    def get_earned_score(self):
        return self._earned_score

    def set_earned_score(self, value):
        try:
            if value is None or str(value).strip() == "":
                self._earned_score = None
            else:
                self._earned_score = float(value)
        except (ValueError, TypeError):
            self._earned_score = None

    def get_max_score(self):
        return self._max_score

    def set_max_score(self, value):
        try:
            if value is None or str(value).strip() == "":
                self._max_score = 100.0
            else:
                self._max_score = float(value)
        except (ValueError, TypeError):
            self._max_score = 100.0

    @property
    def earned_score(self):
        return self._earned_score

    @earned_score.setter
    def earned_score(self, value):
        self.set_earned_score(value)

    @property
    def max_score(self):
        return self._max_score

    @max_score.setter
    def max_score(self, value):
        self.set_max_score(value)

    def get_percentage(self):
        # Calculate score percentage if there is a valid score
        if self._earned_score is None or not self._max_score or self._max_score <= 0:
            return None
        return (self._earned_score / self._max_score) * 100


# Course / Subject class
class Subject:
    def __init__(self, subject_id, name, code, instructor, credit_hours):
        self.subject_id = str(subject_id).strip()
        self.name = str(name).strip()
        self.code = str(code).strip().upper()
        self.instructor = str(instructor).strip()

        try:
            self.credit_hours = int(credit_hours)
        except (ValueError, TypeError):
            self.credit_hours = 3

    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "code": self.code,
            "instructor": self.instructor,
            "credit_hours": self.credit_hours
        }


# Task / Assignment class
class Task(ScoredItem):
    def __init__(self, task_id, title, description, subject_id, due_date, priority="Medium",
                 status="Not Started", earned_score=None, max_score=None, created_at=None):
        super().__init__(earned_score, max_score)
        self.task_id = str(task_id).strip()
        self.title = str(title).strip()
        self.description = str(description).strip()
        self.subject_id = str(subject_id).strip()
        self.due_date = str(due_date).strip()
        self.priority = priority
        self.status = status
        self.created_at = str(created_at).strip() if created_at else date.today().strftime("%Y-%m-%d")

    def get_due_date_object(self):
        try:
            return datetime.strptime(self.due_date, "%Y-%m-%d").date()
        except ValueError:
            return date.today()

    def is_overdue(self):
        if self.status == "Completed":
            return False
        return self.get_due_date_object() < date.today()

    def days_until_due(self):
        return (self.get_due_date_object() - date.today()).days

    def mark_completed(self, earned=None, max_s=None):
        self.status = "Completed"
        if earned is not None:
            self.set_earned_score(earned)
        if max_s is not None:
            self.set_max_score(max_s)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "subject_id": self.subject_id,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "earned_score": self._earned_score,
            "max_score": self._max_score,
            "created_at": self.created_at
        }


# Academic Project class
class Project(ScoredItem):
    def __init__(self, project_id, title, subject_id, deadline, steps=None, phase=None,
                 progress=0, earned_score=None, max_score=100.0, **kwargs):
        super().__init__(earned_score, max_score if max_score is not None else 100.0)
        self.project_id = str(project_id).strip()
        self.title = str(title).strip()
        self.subject_id = str(subject_id).strip()
        self.deadline = str(deadline).strip()

        self.__progress = 0
        self.phase = "Not Started"
        self.steps = []

        # Load project steps and update progress
        if steps and isinstance(steps, list):
            for s in steps:
                self.steps.append({
                    "name": str(s.get("name", "Step")).strip(),
                    "weight": int(s.get("weight", 20)),
                    "max_points": float(s.get("max_points", 20.0)),
                    "earned_points": float(s["earned_points"]) if s.get("earned_points") is not None else None,
                    "completed": bool(s.get("completed", False))
                })
            self.recalculate_status()

    def recalculate_status(self):
        # Update progress, current phase, and total score based on completed steps
        if not self.steps:
            self.__progress = 0
            self.phase = "No Steps Defined"
            return

        total_prog = sum(int(s["weight"]) for s in self.steps if s.get("completed"))
        self.__progress = max(0, min(100, total_prog))

        total_max = sum(float(s.get("max_points", 0.0)) for s in self.steps)
        self._max_score = total_max if total_max > 0 else 100.0

        completed_steps = [s for s in self.steps if s.get("completed")]
        if completed_steps:
            self._earned_score = sum(
                float(s["earned_points"]) if s.get("earned_points") is not None else float(s.get("max_points", 0.0))
                for s in completed_steps
            )
        else:
            self._earned_score = None

        pending_steps = [s for s in self.steps if not s.get("completed")]
        if not pending_steps or self.__progress >= 100:
            self.__progress = 100
            self.phase = "Completed"
        else:
            self.phase = pending_steps[0]["name"]

    def complete_step(self, step_index, earned_points=None):
        if 0 <= step_index < len(self.steps):
            step = self.steps[step_index]
            step["completed"] = True
            if earned_points is not None:
                try:
                    val = float(earned_points)
                    step["earned_points"] = max(0.0, min(val, float(step["max_points"])))
                except ValueError:
                    step["earned_points"] = float(step["max_points"])
            elif step.get("earned_points") is None:
                step["earned_points"] = float(step["max_points"])
            self.recalculate_status()

    def uncomplete_step(self, step_index):
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["completed"] = False
            self.steps[step_index]["earned_points"] = None
            self.recalculate_status()

    def get_progress(self):
        return self.__progress

    @property
    def progress(self):
        return self.__progress

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "title": self.title,
            "subject_id": self.subject_id,
            "deadline": self.deadline,
            "steps": self.steps,
            "phase": self.phase,
            "progress": self.__progress,
            "earned_score": self._earned_score,
            "max_score": self._max_score
        }


# Exam class
class Exam(ScoredItem):
    def __init__(self, exam_id, title, subject_id, exam_date, exam_time="09:00",
                 exam_type="Midterm", earned_score=None, max_score=100.0):
        super().__init__(earned_score, max_score if max_score is not None else 100.0)
        self.exam_id = str(exam_id).strip()
        self.title = str(title).strip()
        self.subject_id = str(subject_id).strip()
        self.exam_date = str(exam_date).strip()
        self.exam_time = str(exam_time).strip()
        self.exam_type = exam_type

    def get_exam_date_object(self):
        try:
            return datetime.strptime(self.exam_date, "%Y-%m-%d").date()
        except ValueError:
            return date.today()

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
            "earned_score": self._earned_score,
            "max_score": self._max_score
        }


# Study Note class
class StudyNote:
    def __init__(self, note_id, title, content, subject_id=None, created_at=None):
        self.note_id = str(note_id).strip()
        self.title = str(title).strip()
        self.content = str(content).strip()
        self.subject_id = str(subject_id).strip() if subject_id else None
        self.created_at = str(created_at).strip() if created_at else date.today().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "note_id": self.note_id,
            "title": self.title,
            "content": self.content,
            "subject_id": self.subject_id,
            "created_at": self.created_at
        }


# User class
class User:
    def __init__(self, username, full_name, major, password):
        self.username = str(username).strip()
        self.full_name = str(full_name).strip()
        self.major = str(major).strip()

        pw_str = str(password).strip()
        # Keep the password if it is already hashed, otherwise hash it
        if len(pw_str) == 64 and all(c in "0123456789abcdef" for c in pw_str.lower()):
            self.__password = pw_str
        else:
            self.__password = self._encrypt_password(pw_str)

    def _encrypt_password(self, raw_password):
        return hashlib.sha256(str(raw_password).strip().encode("utf-8")).hexdigest()

    def check_password(self, input_password):
        return self.__password == self._encrypt_password(input_password)

    def get_password(self):
        return self.__password

    def to_dict(self):
        return {
            "username": self.username,
            "full_name": self.full_name,
            "major": self.major,
            "password": self.__password
        }