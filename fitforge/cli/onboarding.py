from . import ui
from ..core import calculator
from ..core.planner import SPLITS, recommended_split
from ..core.profile import Profile, SEXES, LIFESTYLES, GOALS, EXPERIENCE, EQUIPMENT


def interview(name=None, old=None, name_is_available=None):
    """Ask profile questions; type `back` to revisit the previous answer."""
    d = old.to_dict() if old else {}
    ui.header("Coach interview", "Answer a few questions so I can build your plan.")
    ui.info("Type `back` at a question to return to the previous answer.")
    answers = dict(d)
    if name is not None:
        answers["name"] = name

    fields = []
    if old is None:
        fields.append(("name", lambda: ui.ask(
            "Your name", answers.get("name"), allow_back=True
        )))
    fields.extend([
        ("sex", lambda: ui.ask_choice(
            "Sex (used in the calorie formula):", [(s, s.title()) for s in SEXES],
            answers.get("sex"), allow_back=True
        )),
        ("age", lambda: ui.ask_int(
            "Age", 14, 90, answers.get("age"), allow_back=True
        )),
        ("height_cm", lambda: ui.ask_float(
            "Height (cm)", 120, 230, answers.get("height_cm"), allow_back=True
        )),
        ("weight_kg", lambda: ui.ask_float(
            "Current weight (kg)", 30, 300, answers.get("weight_kg"), allow_back=True
        )),
        ("target_weight_kg", lambda: ui.ask_float(
            "Target weight (kg)", 30, 300,
            answers.get("target_weight_kg", round(answers.get("weight_kg", 70))),
            allow_back=True
        )),
        ("goal", lambda: ui.ask_choice(
            "Main goal:", list(GOALS.items()),
            answers.get("goal", _suggest_goal(answers)), allow_back=True
        )),
        ("lifestyle", lambda: ui.ask_choice(
            "Daily activity outside the gym:",
            [(key, value[0]) for key, value in LIFESTYLES.items()],
            answers.get("lifestyle"), allow_back=True
        )),
        ("experience", lambda: ui.ask_choice(
            "Training experience:", list(EXPERIENCE.items()),
            answers.get("experience"), allow_back=True
        )),
        ("equipment", lambda: ui.ask_choice(
            "Where do you train?", list(EQUIPMENT.items()),
            answers.get("equipment"), allow_back=True
        )),
        ("days_per_week", lambda: ui.ask_int(
            "How many days per week can you train? (1-6)", 1, 6,
            answers.get("days_per_week", 3), allow_back=True
        )),
        ("hours_per_session", lambda: ui.ask_float(
            "How many hours per session? (0.5 - 2.5)", 0.5, 2.5,
            answers.get("hours_per_session", 1), allow_back=True
        )),
        ("split", lambda: _ask_split(answers)),
    ])

    index = 0 if name is None or old is not None else 1
    while index < len(fields):
        key, ask_value = fields[index]
        if key == "sex":
            ui.section("Your body")
        elif key == "goal":
            ui.section("Your goal & lifestyle")
        elif key == "experience":
            ui.section("Your training")
        try:
            value = ask_value()
        except ui.BackRequested:
            if index == 0:
                ui.warn("You're already at the first question.")
            else:
                index -= 1
            continue

        if key == "name" and not value:
            ui.error("Name can't be empty.")
            continue
        if key == "name" and name_is_available and not name_is_available(value):
            ui.error("That name is taken. Pick another one.")
            continue
        answers[key] = value
        if key == "weight_kg" and "height_cm" in answers:
            bmi_now = calculator.bmi(value, answers["height_cm"])
            low, high = calculator.healthy_weight_range(answers["height_cm"])
            ui.info(f"  Your BMI is {bmi_now:.1f} ({calculator.bmi_category(bmi_now)}). "
                    f"Healthy range for your height: {low:.0f}-{high:.0f} kg")
        elif key == "target_weight_kg" and "height_cm" in answers:
            if calculator.bmi(value, answers["height_cm"]) < 18.5:
                ui.warn("That target is below a healthy BMI. I'll keep it, but please reconsider.")
        index += 1

    profile_values = {key: answers[key] for key, _ in fields}
    profile_values["name"] = answers["name"]
    profile = Profile(**profile_values)
    if "created" in d:
        profile.created = d["created"]
    return profile


def _suggest_goal(answers):
    target = answers.get("target_weight_kg", answers.get("weight_kg", 70))
    weight = answers.get("weight_kg", target)
    return "lose" if target < weight - 0.5 else "gain" if target > weight + 0.5 else "maintain"


def _ask_split(answers):
    days = answers.get("days_per_week", 3)
    recommended = recommended_split(days)
    options = [("auto", f"Let the coach decide → {SPLITS[recommended][0]} (recommended)")]
    options += [(key, label) for key, (label, _) in SPLITS.items()]
    return ui.ask_choice("Workout split:", options, answers.get("split", "auto"),
                         allow_back=True)