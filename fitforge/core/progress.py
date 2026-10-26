from datetime import date, timedelta


def week_start(day):
    """Sunday of the week that contains `day` (weeks start on Sunday)."""
    return day - timedelta(days=(day.weekday() + 1) % 7)


def workouts_this_week(workouts, today=None):
    today = today or date.today()
    start = week_start(today)
    return [w for w in workouts if date.fromisoformat(w["date"]) >= start]


def weekly_streak(workouts, days_per_week, today=None):
    """Number of consecutive completed weeks (current week counts if already done)."""
    today = today or date.today()
    per_week = {}
    for w in workouts:
        key = week_start(date.fromisoformat(w["date"]))
        per_week[key] = per_week.get(key, 0) + 1

    streak = 0
    current = week_start(today)
    if per_week.get(current, 0) >= days_per_week:
        streak += 1
    current -= timedelta(days=7)
    while per_week.get(current, 0) >= days_per_week:
        streak += 1
        current -= timedelta(days=7)
    return streak


def totals(workouts):
    return {
        "sessions": len(workouts),
        "minutes": sum(w.get("minutes", 0) for w in workouts),
        "kcal": sum(w.get("kcal", 0) for w in workouts),
        "volume": sum(w.get("volume", 0) for w in workouts),
        "sets": sum(w.get("sets", 0) for w in workouts),
    }


def target_progress(weights, target):
    """Fraction (0..1) of the way from the starting weight to the target."""
    if not weights:
        return 0.0
    start, now = weights[0]["kg"], weights[-1]["kg"]
    total = target - start
    if abs(total) < 0.05:
        return 1.0
    return max(0.0, min(1.0, (now - start) / total))


ACHIEVEMENTS = [
    ("first_rep", "🏁 First Rep", "Finish your first workout"),
    ("five", "🔥 Warming Up", "Finish 5 workouts"),
    ("twenty", "🏋 Iron Habit", "Finish 20 workouts"),
    ("furnace", "⚡ Furnace", "Burn 5,000 kcal in workouts"),
    ("ton", "🦍 Ton Club", "Lift 1,000 kg of volume in one session"),
    ("week", "📅 Perfect Week", "Complete every planned session in a week"),
    ("scale", "⚖ Honest Scale", "Log your weight 3 times"),
    ("halfway", "🎯 Halfway There", "Get halfway to your target weight"),
]


def unlocked(account):
    """Return the set of achievement keys the user has earned."""
    w = account.workouts
    t = totals(w)
    earned = set()
    if t["sessions"] >= 1:
        earned.add("first_rep")
    if t["sessions"] >= 5:
        earned.add("five")
    if t["sessions"] >= 20:
        earned.add("twenty")
    if t["kcal"] >= 5000:
        earned.add("furnace")
    if any(x.get("volume", 0) >= 1000 for x in w):
        earned.add("ton")
    if weekly_streak(w, account.profile.days_per_week) >= 1:
        earned.add("week")
    if len(account.weights) >= 3:
        earned.add("scale")
    if len(account.weights) >= 2 and target_progress(account.weights, account.profile.target_weight_kg) >= 0.5:
        earned.add("halfway")
    return earned
