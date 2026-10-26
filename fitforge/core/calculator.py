from .profile import LIFESTYLES

KCAL_PER_KG_FAT = 7700
GOAL_ADJUSTMENT = {"lose": -500, "maintain": 0, "gain": 300}
EAT_BACK = {"lose": 0.5, "maintain": 1.0, "gain": 1.0}
MIN_CALORIES = {"male": 1500, "female": 1200}


def bmi(weight_kg, height_cm):
    meters = height_cm / 100
    return weight_kg / (meters ** 2)


def bmi_category(value):
    if value < 18.5:
        return "Underweight"
    if value < 25:
        return "Normal"
    if value < 30:
        return "Overweight"
    return "Obese"


def healthy_weight_range(height_cm):
    """Weight range that gives a BMI between 18.5 and 24.9."""
    meters = height_cm / 100
    return 18.5 * meters ** 2, 24.9 * meters ** 2


def bmr(sex, weight_kg, height_cm, age):
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "male" else base - 161


def kcal_per_minute(met, weight_kg):
    return met * 3.5 * weight_kg / 200


def maintenance_calories(profile):
    """Daily calories on a REST day (no workout)."""
    factor = LIFESTYLES[profile.lifestyle][1]
    return bmr(profile.sex, profile.weight_kg, profile.height_cm, profile.age) * factor


def target_calories(profile, workout_burn=0.0):
    """Calories to eat on a given day.

    On training days you "eat back" part of what the workout burns:
    all of it when building muscle / maintaining, half of it when losing fat,
    so the training itself speeds up fat loss.
    """
    eaten_back = workout_burn * EAT_BACK[profile.goal]
    total = maintenance_calories(profile) + eaten_back + GOAL_ADJUSTMENT[profile.goal]
    return max(total, MIN_CALORIES[profile.sex])


def macros(profile, calories):
    """Split calories into protein / fat / carbs (grams)."""
    protein_per_kg = {"lose": 2.0, "maintain": 1.8, "gain": 1.8}[profile.goal]
    protein_g = protein_per_kg * profile.weight_kg
    fat_g = calories * 0.25 / 9
    carbs_g = max(0.0, (calories - protein_g * 4 - fat_g * 9) / 4)
    return {"protein": protein_g, "fat": fat_g, "carbs": carbs_g}


def water_liters(weight_kg, training_minutes=0):
    """~35 ml per kg + 0.5 L for every 30 minutes of training."""
    return weight_kg * 0.035 + 0.5 * (training_minutes / 30)


def weekly_energy_balance(profile, weekly_workout_burn):
    """Average daily calorie surplus (+) / deficit (−) over a week,
    assuming the user eats the target calories and does every session."""
    days = 7
    training_days = profile.days_per_week
    per_session = weekly_workout_burn / training_days if training_days else 0
    total_intake = 0.0
    total_burn = 0.0
    for day in range(days):
        burn = per_session if day < training_days else 0
        total_intake += target_calories(profile, burn)
        total_burn += maintenance_calories(profile) + burn
    return (total_intake - total_burn) / days


def weeks_to_target(profile, weekly_workout_burn):
    """Estimated weeks to reach target weight, or None if not moving that way."""
    diff = profile.target_weight_kg - profile.weight_kg
    if abs(diff) < 0.1:
        return 0.0
    daily = weekly_energy_balance(profile, weekly_workout_burn)
    kg_per_week = daily * 7 / KCAL_PER_KG_FAT
    if kg_per_week == 0 or (diff > 0) != (kg_per_week > 0):
        return None
    return diff / kg_per_week
