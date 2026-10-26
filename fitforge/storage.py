import json
import math
import os
import re
from datetime import date
from pathlib import Path
 
from .core.profile import Profile
 
SAVE_DIR = Path(os.environ.get("FITFORGE_SAVES", Path(__file__).resolve().parent.parent / "saves"))
 

def _slug(name):
    if not isinstance(name, str):
        raise ValueError("Name must be text.")
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "user"
 
 
def path_for(name):
    root = SAVE_DIR.resolve()
    path = root / f"{_slug(name)}.json"
    if path.parent != root:
        raise ValueError("Invalid save filename.")
    return path


class SaveError(ValueError):
    """A save file is missing, unreadable, or structurally invalid."""


def _number(value, label, minimum, maximum):
    try:
        finite = math.isfinite(value)
    except (OverflowError, TypeError):
        finite = False
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not finite or not minimum <= value <= maximum):
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")


def _validate_plan(plan):
    if (not isinstance(plan, dict) or plan.get("split") not in
            ("full_body", "upper_lower", "ppl")
            or not isinstance(plan.get("split_name"), str)):
        raise ValueError("Workout plan is invalid.")
    week = plan.get("week")
    if not isinstance(week, list) or len(week) != 7:
        raise ValueError("Workout plan must contain seven days.")
    for day in week:
        if not isinstance(day, dict) or not isinstance(day.get("day"), str):
            raise ValueError("Workout plan day is invalid.")
        session = day.get("session")
        if session is None:
            continue
        if not isinstance(session, dict) or not isinstance(session.get("type"), str):
            raise ValueError("Workout session is invalid.")
        for key in ("warmup", "cooldown"):
            _number(session.get(key), key, 0, 60)
        exercises = session.get("exercises")
        if not isinstance(exercises, list) or len(exercises) > 20:
            raise ValueError("Workout exercises are invalid.")
        for exercise in exercises:
            if not isinstance(exercise, dict):
                raise ValueError("Workout exercise is invalid.")
            if not isinstance(exercise.get("name"), str) or not exercise["name"]:
                raise ValueError("Workout exercise name is invalid.")
            if not isinstance(exercise.get("muscle"), str):
                raise ValueError("Workout exercise muscle is invalid.")
            if type(exercise.get("sets")) is not int or not 1 <= exercise["sets"] <= 10:
                raise ValueError("Workout exercise sets are invalid.")
            reps = exercise.get("reps")
            match = re.fullmatch(r"(\d{1,3})(?:-(\d{1,3}))?", reps) if isinstance(reps, str) else None
            if not match or any(not 1 <= int(value) <= 100 for value in match.groups() if value):
                raise ValueError("Workout exercise reps are invalid.")
            _number(exercise.get("rest"), "Rest", 0, 600)
            _number(exercise.get("minutes"), "Exercise time", 0, 120)
            _number(exercise.get("met"), "Exercise intensity", 0.1, 30)
        cardio = session.get("cardio")
        if cardio is not None:
            if not isinstance(cardio, dict) or not isinstance(cardio.get("name"), str):
                raise ValueError("Workout cardio is invalid.")
            _number(cardio.get("minutes"), "Cardio time", 0, 120)
            _number(cardio.get("met"), "Cardio intensity", 0.1, 30)


def _read_save(path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SaveError("Save file was not found.") from exc
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SaveError("Save file could not be read.") from exc
    try:
        if not isinstance(payload, dict):
            raise ValueError("Save data must be an object.")
        profile = Profile.from_dict(payload.get("profile"))
        _validate_plan(payload.get("plan"))
        weights = payload.get("weights")
        workouts = payload.get("workouts")
        if not isinstance(weights, list) or not isinstance(workouts, list):
            raise ValueError("Save history is invalid.")
        for entry in weights:
            if not isinstance(entry, dict):
                raise ValueError("Weight history is invalid.")
            date.fromisoformat(entry["date"])
            _number(entry.get("kg"), "Weight entry", 30, 300)
        for workout in workouts:
            if not isinstance(workout, dict) or not isinstance(workout.get("type"), str):
                raise ValueError("Workout history is invalid.")
            date.fromisoformat(workout["date"])
            for key, low, high in (
                ("minutes", 0, 1000), ("kcal", 0, 5000),
                ("sets", 0, 200), ("volume", 0, 100000),
            ):
                _number(workout.get(key), key, low, high)
    except (KeyError, TypeError, ValueError) as exc:
        raise SaveError("Save data is invalid or incomplete.") from exc
    return profile, payload["plan"], weights, workouts

 
def list_users():
    if not SAVE_DIR.exists():
        return []
    names = []
    for file in sorted(SAVE_DIR.glob("*.json")):
        try:
            profile, _, _, _ = _read_save(file)
            names.append(profile.name)
        except SaveError:
            continue
    return names


def list_corrupt_users():
    """Return filename stems for unreadable or invalid save files."""
    if not SAVE_DIR.exists():
        return []
    corrupt = []
    for file in sorted(SAVE_DIR.glob("*.json")):
        try:
            _read_save(file)
        except SaveError:
            corrupt.append(file.stem)
    return corrupt
 
 
def exists(name):
    return path_for(name).exists()
 
 
class Account:
    """A loaded user: profile + plan + history."""
 
    def __init__(self, profile, plan=None, weights=None, workouts=None):
        self.profile = profile
        self.plan = plan
        self.weights = (weights if weights is not None
                        else [{"date": date.today().isoformat(), "kg": profile.weight_kg}])
        self.workouts = workouts if workouts is not None else []
 
    def save(self):
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"profile": self.profile.to_dict(), "plan": self.plan,
                "weights": self.weights, "workouts": self.workouts}
        tmp = path_for(self.profile.name).with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path_for(self.profile.name))
 
    @classmethod
    def load(cls, name):
        return cls(*_read_save(path_for(name)))

    def log_weight(self, kg, when=None):
        when = when or date.today().isoformat()
        _number(kg, "Weight", 30, 300)
        date.fromisoformat(when)
        self.weights = [w for w in self.weights if w["date"] != when]
        self.weights.append({"date": when, "kg": kg})
        self.weights.sort(key=lambda w: w["date"])
        self.profile.weight_kg = self.weights[-1]["kg"]
 
 
def delete(name):
    p = path_for(name)
    if p.exists():
        p.unlink()