"""Exercise catalog used by planning, display, and guided workouts."""

WARMUP_MET = 3.5
COOLDOWN_MET = 2.3

EXERCISES = (
    {"name": "Barbell Squat", "muscle": "quads", "equipment": ("gym",), "compound": True, "met": 5.5, "tip": "Keep your chest tall and knees tracking over your toes."},
    {"name": "Goblet Squat", "muscle": "quads", "equipment": ("gym", "home"), "compound": True, "met": 5.0, "tip": "Hold the weight close to your chest and brace your core."},
    {"name": "Leg Press", "muscle": "quads", "equipment": ("gym",), "compound": True, "met": 5.0, "tip": "Lower with control and avoid locking your knees."},
    {"name": "Dumbbell Step-Up", "muscle": "quads", "equipment": ("gym", "home"), "compound": True, "met": 5.0, "tip": "Push through the whole foot on the raised step."},
    {"name": "Romanian Deadlift", "muscle": "hamstrings", "equipment": ("gym", "home"), "compound": True, "met": 5.5, "tip": "Hinge at the hips and keep the weights close to your legs."},
    {"name": "Lying Leg Curl", "muscle": "hamstrings", "equipment": ("gym",), "compound": False, "met": 3.5, "tip": "Curl smoothly and lower the weight slowly."},
    {"name": "Glute Bridge", "muscle": "glutes", "equipment": ("gym", "home"), "compound": True, "met": 4.0, "tip": "Squeeze your glutes at the top without arching your back."},
    {"name": "Hip Thrust", "muscle": "glutes", "equipment": ("gym", "home"), "compound": True, "met": 5.0, "tip": "Keep your ribs down and finish by squeezing your glutes."},
    {"name": "Standing Calf Raise", "muscle": "calves", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Use a full range of motion and pause at the top."},
    {"name": "Barbell Bench Press", "muscle": "chest", "equipment": ("gym",), "compound": True, "met": 5.0, "tip": "Keep your shoulder blades stable and wrists stacked."},
    {"name": "Dumbbell Bench Press", "muscle": "chest", "equipment": ("gym", "home"), "compound": True, "met": 5.0, "tip": "Lower the weights under control and press evenly."},
    {"name": "Push-Up", "muscle": "chest", "equipment": ("gym", "home"), "compound": True, "met": 4.0, "tip": "Keep a straight line from your head to your heels."},
    {"name": "Incline Dumbbell Press", "muscle": "chest", "equipment": ("gym", "home"), "compound": True, "met": 5.0, "tip": "Use a comfortable incline and avoid flaring your elbows."},
    {"name": "Cable Fly", "muscle": "chest", "equipment": ("gym",), "compound": False, "met": 3.5, "tip": "Bring your hands together with a gentle bend in your elbows."},
    {"name": "Lat Pulldown", "muscle": "back", "equipment": ("gym",), "compound": True, "met": 4.5, "tip": "Pull your elbows down and avoid leaning far back."},
    {"name": "One-Arm Dumbbell Row", "muscle": "back", "equipment": ("gym", "home"), "compound": True, "met": 4.5, "tip": "Pull toward your hip while keeping your back neutral."},
    {"name": "Seated Cable Row", "muscle": "back", "equipment": ("gym",), "compound": True, "met": 4.5, "tip": "Sit tall and squeeze your shoulder blades together."},
    {"name": "Pull-Up", "muscle": "back", "equipment": ("gym", "home"), "compound": True, "met": 6.0, "tip": "Start from a controlled hang and avoid swinging."},
    {"name": "Dumbbell Pullover", "muscle": "back", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Move slowly and keep your ribs from flaring."},
    {"name": "Dumbbell Shoulder Press", "muscle": "shoulders", "equipment": ("gym", "home"), "compound": True, "met": 4.5, "tip": "Brace your core and press without arching your back."},
    {"name": "Lateral Raise", "muscle": "shoulders", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Raise to shoulder height with a slight bend in your elbows."},
    {"name": "Arnold Press", "muscle": "shoulders", "equipment": ("gym", "home"), "compound": True, "met": 4.5, "tip": "Rotate smoothly and use a load you can control."},
    {"name": "Rear Delt Fly", "muscle": "shoulders", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Move your arms out wide and keep your neck relaxed."},
    {"name": "Barbell Curl", "muscle": "biceps", "equipment": ("gym",), "compound": False, "met": 3.5, "tip": "Keep your elbows by your sides and avoid swinging."},
    {"name": "Dumbbell Curl", "muscle": "biceps", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Lower each rep slowly and keep your shoulders relaxed."},
    {"name": "Hammer Curl", "muscle": "biceps", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Keep your palms facing inward throughout the movement."},
    {"name": "Cable Curl", "muscle": "biceps", "equipment": ("gym",), "compound": False, "met": 3.5, "tip": "Keep steady tension and avoid moving your elbows."},
    {"name": "Triceps Pushdown", "muscle": "triceps", "equipment": ("gym",), "compound": False, "met": 3.5, "tip": "Keep your elbows tucked and extend without leaning."},
    {"name": "Overhead Dumbbell Extension", "muscle": "triceps", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Keep your elbows pointing forward and move smoothly."},
    {"name": "Close-Grip Push-Up", "muscle": "triceps", "equipment": ("gym", "home"), "compound": True, "met": 4.0, "tip": "Keep your hands under your shoulders and elbows close."},
    {"name": "Cable Triceps Extension", "muscle": "triceps", "equipment": ("gym",), "compound": False, "met": 3.5, "tip": "Control the return and keep your upper arms still."},
    {"name": "Plank", "muscle": "core", "equipment": ("gym", "home"), "compound": False, "met": 3.0, "tip": "Brace gently and keep your hips level."},
    {"name": "Dead Bug", "muscle": "core", "equipment": ("gym", "home"), "compound": False, "met": 2.8, "tip": "Keep your lower back gently in contact with the floor."},
    {"name": "Cable Crunch", "muscle": "core", "equipment": ("gym",), "compound": False, "met": 3.5, "tip": "Curl your ribs toward your hips without pulling with your arms."},
    {"name": "Bicycle Crunch", "muscle": "core", "equipment": ("gym", "home"), "compound": False, "met": 3.5, "tip": "Rotate through your torso and move at a controlled pace."},
    {"name": "Treadmill Walk", "muscle": "cardio", "equipment": ("gym",), "compound": False, "met": 4.0, "tip": "Choose a pace that lets you maintain a steady conversation."},
    {"name": "Stationary Cycling", "muscle": "cardio", "equipment": ("gym", "home"), "compound": False, "met": 5.0, "tip": "Set a comfortable resistance and keep your cadence steady."},
    {"name": "Brisk Walk", "muscle": "cardio", "equipment": ("gym", "home"), "compound": False, "met": 4.3, "tip": "Walk briskly while keeping your breathing controlled."},
)


def find(name):
    """Return an exercise by case-insensitive name, or None."""
    normalized = name.strip().casefold()
    return next((exercise for exercise in EXERCISES
                 if exercise["name"].casefold() == normalized), None)


def search(query):
    """Return exercises whose name or muscle matches a case-insensitive query."""
    normalized = query.strip().casefold()
    if not normalized:
        return []
    return [exercise for exercise in EXERCISES
            if normalized in exercise["name"].casefold()
            or normalized in exercise["muscle"].casefold()]


def by_muscle(muscle, equipment):
    """Return exercises for a muscle group and available equipment."""
    return [exercise for exercise in EXERCISES
            if exercise["muscle"] == muscle and equipment in exercise["equipment"]]