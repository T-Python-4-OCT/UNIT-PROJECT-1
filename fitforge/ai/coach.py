"""Context-aware personal training advice through the Anthropic Messages API."""

import json
import os
from datetime import date
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from ..core import calculator, planner

SYSTEM_PROMPT = (
    "You are FitForge's friendly personal trainer. Give short, practical, "
    "supportive answers in the same language the user writes in, including Arabic "
    "or English. You are not a doctor: for pain, injuries, or medical conditions, "
    "tell the user to consult a doctor. Never recommend extreme diets or calories "
    "below the app's safe minimum."
)


class CoachError(RuntimeError):
    """The AI coach is unavailable or could not complete a request."""


def build_context(account):
    """Create the current profile, nutrition, plan, and recent-workout context."""
    profile = account.profile
    today_index = (date.today().weekday() + 1) % 7
    today = account.plan["week"][today_index]
    session = today["session"]
    burn = planner.session_calories(session, profile.weight_kg)["total"] if session else 0
    calories = calculator.target_calories(profile, burn)
    macros = calculator.macros(profile, calories)
    weekly_plan = []
    for day in account.plan["week"]:
        workout = day["session"]
        weekly_plan.append({
            "day": day["day"],
            "session": None if workout is None else {
                "type": workout["type"],
                "exercises": [
                    {"name": item["name"], "sets": item["sets"], "reps": item["reps"]}
                    for item in workout["exercises"]
                ],
            },
        })

    return {
        "profile": {
            "age": profile.age,
            "sex": profile.sex,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "target_weight_kg": profile.target_weight_kg,
            "goal": profile.goal,
            "experience": profile.experience,
            "equipment": profile.equipment,
            "days_per_week": profile.days_per_week,
            "hours_per_session": profile.hours_per_session,
        },
        "today": {
            "day": today["day"],
            "session": session["type"] if session else "rest",
            "calories_kcal": calories,
            "safe_minimum_calories_kcal": calculator.MIN_CALORIES[profile.sex],
            "macros_g": macros,
        },
        "weekly_plan": weekly_plan,
        "last_5_workouts": sorted(
            account.workouts, key=lambda workout: workout["date"], reverse=True
        )[:5],
    }


class AICoach:
    """Keep one chat history and send fresh trainee context with each turn."""

    def __init__(self, client=None, model=None, api_key=None):
        project_root = Path(__file__).resolve().parents[2]
        load_dotenv(project_root / ".env")
        self.api_key = api_key if api_key is not None else os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("FITFORGE_MODEL", "claude-sonnet-5-5")
        self.client = client
        self.history = []

    def _get_client(self):
        if self.client is None:
            if not self.api_key:
                raise CoachError(
                    "AI Coach needs ANTHROPIC_API_KEY. Add it to .env or your environment; "
                    "all other FitForge features will keep working."
                )
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except anthropic.APIError as exc:
                raise CoachError("AI Coach could not connect. Please try again later.") from exc
        return self.client

    def ask(self, question, account):
        """Ask a question, preserving chat history if the request succeeds."""
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Please enter a question.")

        context = json.dumps(build_context(account), ensure_ascii=False, indent=2)
        messages = self.history + [{
            "role": "user",
            "content": f"Trainee context for this turn:\n{context}\n\nQuestion: {question.strip()}",
        }]
        try:
            response = self._get_client().messages.create(
                model=self.model,
                max_tokens=600,
                system=SYSTEM_PROMPT,
                messages=messages,
            )
        except anthropic.APIError as exc:
            raise CoachError(
                "AI Coach is temporarily unavailable. Check your connection and try again."
            ) from exc

        answer = "\n".join(
            block.text for block in response.content
            if getattr(block, "type", None) == "text"
        ).strip()
        if not answer:
            raise CoachError("AI Coach returned an empty answer. Please try again.")
        self.history = messages + [{"role": "assistant", "content": answer}]
        return answer
