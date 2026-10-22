from datetime import datetime, date

class Subject:
    def __init__(self, subject_id, name, code, instructor, credit_hours):
        self.subject_id = str(subject_id).strip()
        self.name = str(name).strip()
        self.code = str(code).strip().upper()
        self.instructor = str(instructor).strip()
        
        # Try-except for safe integer conversion
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
        
        # Private attributes to secure scores
        self.__earned_score = None
        self.__max_score = None
        
        if earned_score is not None:
            self.set_earned_score(earned_score)
        if max_score is not None:
            self.set_max_score(max_score)
            
        self.created_at = str(created_at).strip() if created_at else date.today().strftime("%Y-%m-%d")

    # Getter and Setter for earned score
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

    # Getter and Setter for max score
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

    # Properties to allow clean access
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

class Exam:
    def __init__(self, exam_id, title, subject_id, exam_date, exam_time="09:00", exam_type="Midterm", earned_score=None, max_score=100.0):
        self.exam_id = str(exam_id).strip()
        self.title = str(title).strip()
        self.subject_id = str(subject_id).strip()
        self.exam_date = str(exam_date).strip()
        self.exam_time = str(exam_time).strip()
        self.exam_type = exam_type
        
        self.__earned_score = float(earned_score) if earned_score is not None and str(earned_score).strip() != "" else None
        self.__max_score = float(max_score) if max_score is not None else 100.0

    @property
    def earned_score(self):
        return self.__earned_score

    @earned_score.setter
    def earned_score(self, value):
        try:
            self.__earned_score = float(value) if value is not None and str(value).strip() != "" else None
        except ValueError:
            self.__earned_score = None

    @property
    def max_score(self):
        return self.__max_score

    @max_score.setter
    def max_score(self, value):
        try:
            self.__max_score = float(value) if value is not None else 100.0
        except ValueError:
            self.__max_score = 100.0

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
    