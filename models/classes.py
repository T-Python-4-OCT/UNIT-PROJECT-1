from datetime import datetime, date

class Subject:
    def __init__(self, subject_id, name, code, instructor, credit_hours):
        self.subject_id = str(subject_id).strip()
        self.name = str(name).strip()
        self.code = str(code).strip().upper()
        self.instructor = str(instructor).strip()
        
        try:
            self.credit_hours = int(credit_hours)
        except ValueError:
            self.credit_hours = 3

    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "code": self.code,
            "instructor": self.instructor,
            "credit_hours": self.credit_hours
        }


class Task:
    def __init__(self, task_id, title, description, subject_id, due_date, priority="Medium", status="Not Started", earned_score=None, max_score=None, created_at=None):
        self.task_id = str(task_id).strip()
        self.title = str(title).strip()
        self.description = str(description).strip()
        self.subject_id = str(subject_id).strip()
        self.due_date = str(due_date).strip()
        self.priority = priority
        self.status = status
        
        self.__earned_score = None
        self.__max_score = None
        
        if earned_score is not None:
            self.set_earned_score(earned_score)
        if max_score is not None:
            self.set_max_score(max_score)
            
        self.created_at = str(created_at).strip() if created_at else date.today().strftime("%Y-%m-%d")

    def get_earned_score(self):
        return self.__earned_score

    def set_earned_score(self, score):
        try:
            if score is None or str(score).strip() == "":
                self.__earned_score = None
            else:
                self.__earned_score = float(score)
        except ValueError:
            self.__earned_score = None

    def get_max_score(self):
        return self.__max_score

    def set_max_score(self, score):
        try:
            if score is None or str(score).strip() == "":
                self.__max_score = 100.0
            else:
                self.__max_score = float(score)
        except ValueError:
            self.__max_score = 100.0

    @property
    def earned_score(self):
        return self.__earned_score

    @earned_score.setter
    def earned_score(self, value):
        self.set_earned_score(value)

    @property
    def max_score(self):
        return self.__max_score

    @max_score.setter
    def max_score(self, value):
        self.set_max_score(value)

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
            "earned_score": self.__earned_score,
            "max_score": self.__max_score,
            "created_at": self.created_at
        }


class Project:
    def __init__(self, project_id, title, subject_id, deadline, steps=None, phase=None, progress=0, earned_score=None, max_score=100.0, **kwargs):
        self.project_id = str(project_id).strip()
        self.title = str(title).strip()
        self.subject_id = str(subject_id).strip()
        self.deadline = str(deadline).strip()
        
        self.__progress = 0
        self.__earned_score = None
        self.__max_score = 100.0
        self.phase = "Not Started"
        self.steps = []

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
        else:
            self.set_earned_score(earned_score)
            self.set_max_score(max_score)

    def recalculate_status(self):
        """Automatically calculate total progress %, current phase, and total score from custom steps."""
        if not self.steps:
            self.__progress = 0
            self.phase = "No Steps Defined"
            return

        total_prog = sum(int(s["weight"]) for s in self.steps if s.get("completed"))
        self.__progress = max(0, min(100, total_prog))

        total_max = sum(float(s.get("max_points", 0.0)) for s in self.steps)
        self.__max_score = total_max if total_max > 0 else 100.0

        completed_steps = [s for s in self.steps if s.get("completed")]
        if completed_steps:
            self.__earned_score = sum(
                float(s["earned_points"]) if s.get("earned_points") is not None else float(s.get("max_points", 0.0))
                for s in completed_steps
            )
        else:
            self.__earned_score = None

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

    def get_earned_score(self):
        return self.__earned_score

    def set_earned_score(self, value):
        try:
            if value is None or str(value).strip() == "":
                self.__earned_score = None
            else:
                self.__earned_score = float(value)
        except ValueError:
            self.__earned_score = None

    def get_max_score(self):
        return self.__max_score

    def set_max_score(self, value):
        try:
            if value is None or str(value).strip() == "":
                self.__max_score = 100.0
            else:
                self.__max_score = float(value)
        except ValueError:
            self.__max_score = 100.0

    @property
    def progress(self):
        return self.__progress

    @property
    def earned_score(self):
        return self.__earned_score

    @earned_score.setter
    def earned_score(self, value):
        self.set_earned_score(value)

    @property
    def max_score(self):
        return self.__max_score

    @max_score.setter
    def max_score(self, value):
        self.set_max_score(value)

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "title": self.title,
            "subject_id": self.subject_id,
            "deadline": self.deadline,
            "steps": self.steps,
            "phase": self.phase,
            "progress": self.__progress,
            "earned_score": self.__earned_score,
            "max_score": self.__max_score
        }


class Exam:
    def __init__(self, exam_id, title, subject_id, exam_date, exam_time="09:00", exam_type="Midterm", earned_score=None, max_score=100.0):
        self.exam_id = str(exam_id).strip()
        self.title = str(title).strip()
        self.subject_id = str(subject_id).strip()
        self.exam_date = str(exam_date).strip()
        self.exam_time = str(exam_time).strip()
        self.exam_type = exam_type
        
        self.__earned_score = None
        self.__max_score = 100.0
        
        self.set_earned_score(earned_score)
        self.set_max_score(max_score)

    def get_earned_score(self):
        return self.__earned_score

    def set_earned_score(self, value):
        try:
            if value is None or str(value).strip() == "":
                self.__earned_score = None
            else:
                self.__earned_score = float(value)
        except ValueError:
            self.__earned_score = None

    def get_max_score(self):
        return self.__max_score

    def set_max_score(self, value):
        try:
            if value is None or str(value).strip() == "":
                self.__max_score = 100.0
            else:
                self.__max_score = float(value)
        except ValueError:
            self.__max_score = 100.0

    @property
    def earned_score(self):
        return self.__earned_score

    @earned_score.setter
    def earned_score(self, value):
        self.set_earned_score(value)

    @property
    def max_score(self):
        return self.__max_score

    @max_score.setter
    def max_score(self, value):
        self.set_max_score(value)

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
            "earned_score": self.__earned_score,
            "max_score": self.__max_score
        }


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


class User:
    def __init__(self, username, full_name, major, password):
        self.username = str(username).strip()
        self.full_name = str(full_name).strip()
        self.major = str(major).strip()
        self.__password = str(password).strip()

    def check_password(self, input_password):
        return self.__password == str(input_password).strip()

    def get_password(self):
        return self.__password

    def to_dict(self):
        return {
            "username": self.username,
            "full_name": self.full_name,
            "major": self.major,
            "password": self.__password
        }