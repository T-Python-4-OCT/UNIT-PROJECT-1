from dataclasses import dataclass, field, asdict
from datetime import date

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

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    @property
    def session_minutes(self):
        return int(round(self.hours_per_session * 60))
