from dataclasses import dataclass, field, asdict
from datetime import date
import math

SEXES = ("male", "female")

# Non-exercise daily activity (job / lifestyle). Workouts are added separately.
LIFESTYLES = {
    "sedentary": ("Desk job, little walking", 1.2),
    "light": ("Some walking / standing during the day", 1.375),
    "active": ("On your feet most of the day", 1.55),
}

GOALS = {
    "lose": "Lose fat",
    "maintain": "Stay fit / recomposition",
    "gain": "Build muscle",
}

EXPERIENCE = {
    "beginner": "Less than 6 months of training",
    "intermediate": "6 months - 2 years",
    "advanced": "More than 2 years",
}

EQUIPMENT = {
    "gym": "Full gym (barbells, machines, cables)",
    "home": "Home (dumbbells + bodyweight)",
}


@dataclass
class Profile:
    name: str
    sex: str
    age: int
    height_cm: float
    weight_kg: float
    target_weight_kg: float
    lifestyle: str = "sedentary"
    goal: str = "maintain"
    experience: str = "beginner"
    equipment: str = "gym"
    days_per_week: int = 3
    hours_per_session: float = 1.0
    split: str = "auto"
    created: str = field(default_factory=lambda: date.today().isoformat())

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Name must not be empty.")
        if not isinstance(self.sex, str) or self.sex not in SEXES:
            raise ValueError("Sex must be male or female.")
        if type(self.age) is not int or not 14 <= self.age <= 90:
            raise ValueError("Age must be a whole number between 14 and 90.")
        for label, value, minimum, maximum in (
            ("Height", self.height_cm, 120, 230),
            ("Weight", self.weight_kg, 30, 300),
            ("Target weight", self.target_weight_kg, 30, 300),
        ):
            try:
                finite = math.isfinite(value)
            except (OverflowError, TypeError):
                finite = False
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not finite or not minimum <= value <= maximum):
                raise ValueError(f"{label} must be between {minimum} and {maximum}.")
        if not isinstance(self.lifestyle, str) or self.lifestyle not in LIFESTYLES:
            raise ValueError("Choose a supported activity level.")
        if not isinstance(self.goal, str) or self.goal not in GOALS:
            raise ValueError("Choose a supported goal.")
        if not isinstance(self.experience, str) or self.experience not in EXPERIENCE:
            raise ValueError("Choose a supported experience level.")
        if not isinstance(self.equipment, str) or self.equipment not in EQUIPMENT:
            raise ValueError("Choose gym or home equipment.")
        if type(self.days_per_week) is not int or not 1 <= self.days_per_week <= 6:
            raise ValueError("Training days must be a whole number from 1 to 6.")
        try:
            finite_hours = math.isfinite(self.hours_per_session)
        except (OverflowError, TypeError):
            finite_hours = False
        if (isinstance(self.hours_per_session, bool)
                or not isinstance(self.hours_per_session, (int, float))
                or not finite_hours or not 0.5 <= self.hours_per_session <= 2.5):
            raise ValueError("Session length must be between 0.5 and 2.5 hours.")
        if not isinstance(self.split, str) or self.split not in ("auto", "full_body", "upper_lower", "ppl"):
            raise ValueError("Choose a supported workout split.")
        if not isinstance(self.created, str):
            raise ValueError("Profile creation date must be an ISO date.")
        try:
            date.fromisoformat(self.created)
        except (TypeError, ValueError) as exc:
            raise ValueError("Profile creation date must be an ISO date.") from exc

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("Profile data must be an object.")
        required = {"name", "sex", "age", "height_cm", "weight_kg", "target_weight_kg"}
        if not required.issubset(data):
            raise ValueError("Profile data is missing required fields.")
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    @property
    def session_minutes(self):
        return int(round(self.hours_per_session * 60))
