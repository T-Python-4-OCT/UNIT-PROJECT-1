from . import calculator
from ..data import exercises as db

WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

SPLITS = {
    "full_body": ("Full Body", ["Full Body A", "Full Body B"]),
    "upper_lower": ("Upper / Lower", ["Upper", "Lower"]),
    "ppl": ("Push / Pull / Legs", ["Push", "Pull", "Legs"]),
}

# Ordered by priority: the planner takes as many slots as the time allows.
# "=Name" means that exact exercise.
DAY_SLOTS = {
    "Full Body A": ["quads", "chest", "back", "shoulders", "hamstrings", "biceps", "triceps",
                    "core", "calves", "glutes"],
    "Full Body B": ["hamstrings", "back", "chest", "quads", "shoulders", "triceps", "biceps",
                    "core", "glutes", "calves"],
    "Upper": ["chest", "back", "shoulders", "back", "chest", "biceps", "triceps",
              "=Rear Delt Fly", "shoulders", "core"],
    "Lower": ["quads", "hamstrings", "glutes", "quads", "hamstrings", "calves", "core",
              "quads", "core"],
    "Push": ["chest", "shoulders", "chest", "triceps", "shoulders", "triceps", "chest",
             "shoulders", "core"],
    "Pull": ["back", "back", "biceps", "=Rear Delt Fly", "back", "biceps", "back",
             "biceps", "core"],
    "Legs": ["quads", "hamstrings", "quads", "glutes", "hamstrings", "calves", "core",
             "quads", "core"],
}

# Which weekdays (0 = Sunday) to train for N days per week.
SCHEDULES = {
    1: [0],
    2: [0, 3],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 4, 5],
    6: [0, 1, 2, 3, 4, 5],
}

WORK_SECONDS_PER_SET = 40
WARMUP_MIN = 8
COOLDOWN_MIN = 5


def recommended_split(days_per_week):
    if days_per_week <= 3:
        return "full_body"
    if days_per_week == 4:
        return "upper_lower"
    return "ppl"


def prescription(goal, experience, compound):
    """Return (sets, reps, rest_seconds) for an exercise."""
    if goal == "lose":
        sets, reps, rest = (3, "8-12", 75) if compound else (3, "12-15", 60)
    elif goal == "gain":
        sets, reps, rest = (4, "6-10", 120) if compound else (3, "10-12", 75)
    else:
        sets, reps, rest = (3, "8-10", 90) if compound else (3, "10-12", 60)

    if experience == "beginner":
        sets = min(sets, 3)
    elif experience == "advanced" and compound:
        sets += 1
    return sets, reps, rest


def exercise_minutes(sets, rest_seconds):
    return sets * (WORK_SECONDS_PER_SET + rest_seconds) / 60


def _pick(slot, equipment, used, variant):
    """Choose an exercise for a slot that isn't used yet in this session."""
    if slot.startswith("="):
        ex = db.find(slot[1:])
        if ex and equipment in ex["equipment"] and ex["name"] not in used:
            return ex
        slot = ex["muscle"] if ex else "shoulders"
    pool = db.by_muscle(slot, equipment)
    if not pool:
        return None
    for i in range(len(pool)):
        candidate = pool[(variant + i) % len(pool)]
        if candidate["name"] not in used:
            return candidate
    return None


def build_session(day_type, profile, variant=0):
    """Create one training session that fits in the user's available time."""
    total = profile.session_minutes
    cardio_min = 0
    if profile.goal == "lose" and total >= 45:
        cardio_min = min(20, round(total * 0.2))
    elif total >= 90:
        cardio_min = 10
    lifting_budget = total - WARMUP_MIN - COOLDOWN_MIN - cardio_min

    items, used, spent = [], set(), 0.0
    for slot in DAY_SLOTS[day_type]:
        ex = _pick(slot, profile.equipment, used, variant)
        if ex is None:
            continue
        sets, reps, rest = prescription(profile.goal, profile.experience, ex["compound"])
        minutes = round(exercise_minutes(sets, rest), 1)
        if spent + minutes > lifting_budget and len(items) >= 3:
            break
        used.add(ex["name"])
        spent += minutes
        items.append({"name": ex["name"], "muscle": ex["muscle"], "sets": sets,
                      "reps": reps, "rest": rest, "minutes": minutes, "met": ex["met"],
                      "compound": ex["compound"]})

    # Long sessions: add extra sets (compounds first, max 5 sets each).
    max_sets = 4 if profile.experience == "beginner" else 5
    added = True
    while added:
        added = False
        for item in sorted(items, key=lambda i: not i["compound"]):
            one_set = round(exercise_minutes(1, item["rest"]), 1)
            if item["sets"] < max_sets and spent + one_set <= lifting_budget - 5:
                item["sets"] += 1
                item["minutes"] = round(exercise_minutes(item["sets"], item["rest"]), 1)
                spent += one_set
                added = True
    for item in items:
        del item["compound"]
    spent = sum(item["minutes"] for item in items)

    # Whatever time is still left goes to cardio.
    leftover = lifting_budget - spent
    if leftover >= 5:
        cap = 30 if profile.goal == "lose" else 15
        cardio_min = min(cap, cardio_min + int(leftover))

    cardio = None
    if cardio_min:
        options = db.by_muscle("cardio", profile.equipment)
        choice = options[variant % len(options)]
        cardio = {"name": choice["name"], "minutes": cardio_min, "met": choice["met"]}

    return {"type": day_type, "warmup": WARMUP_MIN, "cooldown": COOLDOWN_MIN,
            "exercises": items, "cardio": cardio}


def build_plan(profile):
    split = profile.split if profile.split in SPLITS else recommended_split(profile.days_per_week)
    split_name, rotation = SPLITS[split]
    days = min(max(profile.days_per_week, 1), 6)
    schedule = SCHEDULES[days]

    week = []
    session_index = 0
    for i, weekday in enumerate(WEEKDAYS):
        if i in schedule:
            day_type = rotation[session_index % len(rotation)]
            variant = session_index // len(rotation)
            week.append({"day": weekday, "session": build_session(day_type, profile, variant)})
            session_index += 1
        else:
            week.append({"day": weekday, "session": None})
    return {"split": split, "split_name": split_name, "week": week}


# ------------------------------------------------------------ calculations

def session_minutes(session):
    lifting = sum(item["minutes"] for item in session["exercises"])
    cardio = session["cardio"]["minutes"] if session["cardio"] else 0
    return session["warmup"] + lifting + cardio + session["cooldown"]


def session_calories(session, weight_kg):
    """Breakdown of calories burned in a session (kcal)."""
    warm = calculator.kcal_per_minute(db.WARMUP_MET, weight_kg) * session["warmup"]
    cool = calculator.kcal_per_minute(db.COOLDOWN_MET, weight_kg) * session["cooldown"]
    lifting = sum(calculator.kcal_per_minute(i["met"], weight_kg) * i["minutes"]
                  for i in session["exercises"])
    cardio = 0.0
    if session["cardio"]:
        c = session["cardio"]
        cardio = calculator.kcal_per_minute(c["met"], weight_kg) * c["minutes"]
    return {"warmup": warm, "lifting": lifting, "cardio": cardio,
            "cooldown": cool, "total": warm + lifting + cardio + cool}


def weekly_burn(plan, weight_kg):
    return sum(session_calories(d["session"], weight_kg)["total"]
               for d in plan["week"] if d["session"])


def find_day(plan, text):
    """Find a plan day by weekday name (or prefix) or session type."""
    text = text.strip().lower()
    for d in plan["week"]:
        if d["day"].lower().startswith(text) and len(text) >= 2:
            return d
    for d in plan["week"]:
        if d["session"] and d["session"]["type"].lower() == text:
            return d
    return None


def swap_exercise(plan, old_name, new_name, profile):
    """Replace an exercise everywhere in the plan. Returns how many were swapped."""
    new = db.find(new_name)
    if new is None:
        raise ValueError(f"'{new_name}' is not in the exercise library.")
    if profile.equipment not in new["equipment"]:
        raise ValueError(f"'{new['name']}' needs equipment you don't have ({profile.equipment}).")
    count = 0
    for d in plan["week"]:
        if not d["session"]:
            continue
        for item in d["session"]["exercises"]:
            if item["name"].lower() == old_name.strip().lower():
                sets, reps, rest = prescription(profile.goal, profile.experience, new["compound"])
                item.update({"name": new["name"], "muscle": new["muscle"], "sets": sets, "reps": reps,
                             "rest": rest, "minutes": round(exercise_minutes(sets, rest), 1),
                             "met": new["met"]})
                count += 1
    return count