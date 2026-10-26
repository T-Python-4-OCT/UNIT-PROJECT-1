import contextlib
import io
import json
import os
import tempfile
import unittest
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import anthropic
from fitforge.core import calculator, planner
from fitforge.core.profile import Profile
from fitforge.data import exercises as db
from fitforge import storage
from fitforge.cli.session import _parse_reps
from fitforge.cli import views
from fitforge.cli.shell import Shell
from fitforge.cli.onboarding import interview
from fitforge.ai.coach import AICoach, CoachError, build_context


def make_profile(**changes):
    base = Profile(name="Test", sex="male", age=25, height_cm=180, weight_kg=90,
                   target_weight_kg=80, lifestyle="sedentary", goal="lose",
                   experience="intermediate", equipment="gym",
                   days_per_week=4, hours_per_session=1.0)
    return replace(base, **changes)


class CalculatorTests(unittest.TestCase):
    def test_bmi(self):
        self.assertAlmostEqual(calculator.bmi(90, 180), 27.78, places=2)
        self.assertEqual(calculator.bmi_category(27.78), "Overweight")

    def test_bmr_mifflin(self):
        # 10*90 + 6.25*180 - 5*25 + 5 = 1905
        self.assertAlmostEqual(calculator.bmr("male", 90, 180, 25), 1905)
        self.assertAlmostEqual(calculator.bmr("female", 90, 180, 25), 1739)

    def test_kcal_per_minute(self):
        # MET 6, 90 kg -> 6*3.5*90/200 = 9.45
        self.assertAlmostEqual(calculator.kcal_per_minute(6, 90), 9.45)

    def test_calorie_floor(self):
        p = make_profile(sex="female", weight_kg=45, height_cm=150, age=60, target_weight_kg=40)
        self.assertGreaterEqual(calculator.target_calories(p), 1200)

    def test_lose_goal_reaches_target(self):
        p = make_profile()
        weeks = calculator.weeks_to_target(p, weekly_workout_burn=2000)
        self.assertIsNotNone(weeks)
        self.assertGreater(weeks, 0)

    def test_training_makes_fat_loss_faster(self):
        p = make_profile()
        self.assertLess(calculator.weeks_to_target(p, 3000), calculator.weeks_to_target(p, 0))

    def test_wrong_direction_returns_none(self):
        p = make_profile(goal="gain")  # target is lower than current weight
        self.assertIsNone(calculator.weeks_to_target(p, 2000))


class PlannerTests(unittest.TestCase):
    def test_recommended_split(self):
        self.assertEqual(planner.recommended_split(3), "full_body")
        self.assertEqual(planner.recommended_split(4), "upper_lower")
        self.assertEqual(planner.recommended_split(6), "ppl")

    def test_plan_has_right_number_of_sessions(self):
        for days in range(1, 7):
            plan = planner.build_plan(make_profile(days_per_week=days))
            sessions = [d for d in plan["week"] if d["session"]]
            self.assertEqual(len(sessions), days)
            self.assertEqual(len(plan["week"]), 7)

    def test_session_fits_time(self):
        for hours in (0.5, 1.0, 1.5, 2.0):
            p = make_profile(hours_per_session=hours)
            for d in planner.build_plan(p)["week"]:
                if d["session"]:
                    # at least 3 exercises are always kept, so allow a small overflow on short sessions
                    limit = p.session_minutes + (15 if hours < 1 else 0)
                    self.assertLessEqual(planner.session_minutes(d["session"]), limit)

    def test_no_duplicate_exercises_in_a_session(self):
        plan = planner.build_plan(make_profile(days_per_week=6, hours_per_session=2))
        for d in plan["week"]:
            if d["session"]:
                names = [i["name"] for i in d["session"]["exercises"]]
                self.assertEqual(len(names), len(set(names)))

    def test_home_plan_uses_home_equipment_only(self):
        plan = planner.build_plan(make_profile(equipment="home", days_per_week=5))
        for d in plan["week"]:
            if d["session"]:
                for item in d["session"]["exercises"]:
                    self.assertIn("home", db.find(item["name"])["equipment"])

    def test_swap(self):
        p = make_profile(days_per_week=6, split="ppl")
        plan = planner.build_plan(p)
        first = next(d for d in plan["week"] if d["session"])["session"]["exercises"][0]["name"]
        count = planner.swap_exercise(plan, first, "Push-Up", p)
        self.assertGreaterEqual(count, 1)
        with self.assertRaises(ValueError):
            planner.swap_exercise(plan, "Push-Up", "Flying Kick", p)

    def test_calories_positive(self):
        p = make_profile()
        plan = planner.build_plan(p)
        self.assertGreater(planner.weekly_burn(plan, p.weight_kg), 0)


class InputAndSaveSafetyTests(unittest.TestCase):
    def test_profile_rejects_out_of_range_values(self):
        with self.assertRaises(ValueError):
            make_profile(age=13)
        with self.assertRaises(ValueError):
            make_profile(height_cm=231)
        with self.assertRaises(ValueError):
            make_profile(weight_kg=301)
        with self.assertRaises(ValueError):
            make_profile(days_per_week=7)
        with self.assertRaises(ValueError):
            make_profile(hours_per_session=float("inf"))

    def test_reps_are_bounded(self):
        self.assertEqual(_parse_reps("8"), 8)
        self.assertEqual(_parse_reps("100"), 100)
        for invalid in ("0", "101", "-1", "abc", ""):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                _parse_reps(invalid)

    def test_user_names_cannot_escape_save_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(storage, "SAVE_DIR", Path(directory)):
                path = storage.path_for("../../outside")
                self.assertEqual(path.parent, Path(directory).resolve())
                self.assertEqual(path.name, "outside.json")

    def test_corrupt_save_is_reported_and_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(storage, "SAVE_DIR", Path(directory)):
                (Path(directory) / "broken.json").write_text("{", encoding="utf-8")
                self.assertEqual(storage.list_users(), [])
                self.assertEqual(storage.list_corrupt_users(), ["broken"])
                with self.assertRaises(storage.SaveError):
                    storage.Account.load("broken")

    def test_hand_edited_save_with_invalid_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(storage, "SAVE_DIR", Path(directory)):
                account = storage.Account(make_profile(), planner.build_plan(make_profile()))
                account.save()
                path = storage.path_for("Test")
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["profile"]["weight_kg"] = 900
                path.write_text(json.dumps(payload), encoding="utf-8")
                self.assertEqual(storage.list_corrupt_users(), ["test"])
                with self.assertRaises(storage.SaveError):
                    storage.Account.load("Test")
                payload["profile"]["weight_kg"] = 10 ** 1000
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(storage.SaveError):
                    storage.Account.load("Test")

    def test_logged_weight_is_bounded(self):
        account = storage.Account(make_profile())
        for invalid in (0, 301, float("nan")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                account.log_weight(invalid)


class CliViewTests(unittest.TestCase):
    def test_existing_progress_commands_render_without_errors(self):
        profile = make_profile()
        account = storage.Account(profile, planner.build_plan(profile))
        for show in (views.show_progress, views.show_forecast, views.show_achievements):
            with self.subTest(view=show.__name__), contextlib.redirect_stdout(io.StringIO()):
                show(account)


class AICoachTests(unittest.TestCase):
    def make_account(self):
        profile = make_profile()
        account = storage.Account(profile, planner.build_plan(profile))
        account.workouts = [
            {"date": (date.today() - timedelta(days=offset)).isoformat(),
             "type": "Full Body", "minutes": 45, "kcal": 300, "sets": 20, "volume": 1200}
            for offset in range(7)
        ]
        return account

    def test_context_has_profile_nutrition_plan_and_five_recent_workouts(self):
        context = build_context(self.make_account())
        self.assertEqual(context["profile"]["age"], 25)
        self.assertIn("calories_kcal", context["today"])
        self.assertIn("protein", context["today"]["macros_g"])
        self.assertEqual(len(context["weekly_plan"]), 7)
        self.assertEqual(len(context["last_5_workouts"]), 5)
        self.assertGreaterEqual(
            context["last_5_workouts"][0]["date"],
            context["last_5_workouts"][-1]["date"],
        )

    def test_messages_api_keeps_chat_history_and_refreshes_context(self):
        client = Mock()
        client.messages.create.side_effect = [
            SimpleNamespace(content=[SimpleNamespace(type="text", text="First answer")]),
            SimpleNamespace(content=[SimpleNamespace(type="text", text="Second answer")]),
        ]
        coach = AICoach(client=client, model="test-model")
        account = self.make_account()

        self.assertEqual(coach.ask("What should I eat?", account), "First answer")
        self.assertEqual(coach.ask("And after training?", account), "Second answer")

        first_messages = client.messages.create.call_args_list[0].kwargs["messages"]
        second_messages = client.messages.create.call_args_list[1].kwargs["messages"]
        self.assertEqual(len(first_messages), 1)
        self.assertEqual(len(second_messages), 3)
        self.assertIn("Trainee context for this turn", second_messages[-1]["content"])
        self.assertEqual(client.messages.create.call_args.kwargs["model"], "test-model")
        self.assertIn("same language", client.messages.create.call_args.kwargs["system"])

    def test_missing_key_is_friendly_and_does_not_make_a_request(self):
        with patch("fitforge.ai.coach.load_dotenv"), patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": ""}
        ):
            coach = AICoach()
        with self.assertRaisesRegex(CoachError, "ANTHROPIC_API_KEY"):
            coach.ask("Help me plan lunch.", self.make_account())

    def test_model_uses_environment_override(self):
        with patch("fitforge.ai.coach.load_dotenv"), patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "", "FITFORGE_MODEL": "claude-test"}
        ):
            self.assertEqual(AICoach().model, "claude-test")

    def test_api_failure_becomes_a_friendly_coach_error(self):
        client = Mock()
        client.messages.create.side_effect = anthropic.APIError(
            "network unavailable", request=None, body=None
        )
        coach = AICoach(client=client)
        with self.assertRaisesRegex(CoachError, "temporarily unavailable"):
            coach.ask("How was my week?", self.make_account())
        self.assertEqual(coach.history, [])

    def test_blank_question_is_rejected_without_request(self):
        client = Mock()
        coach = AICoach(client=client)
        with self.assertRaises(ValueError):
            coach.ask(" ", self.make_account())
        client.messages.create.assert_not_called()

    def test_cli_continues_after_missing_key(self):
        with patch("fitforge.ai.coach.load_dotenv"), patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": ""}
        ):
            shell = Shell()
            shell.account = self.make_account()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                shell.cmd_ask("What should I eat today?")
                shell.cmd_plan("")
        self.assertIn("ANTHROPIC_API_KEY", output.getvalue())
        self.assertIn("Weekly plan", output.getvalue())
        self.assertTrue(shell.running)


class OnboardingGuidanceTests(unittest.TestCase):
    def test_profile_setup_prints_first_steps_and_recreates_named_profile(self):
        profile = make_profile(name="Recreated")
        shell = Shell()
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(storage, "SAVE_DIR", Path(directory)),
                patch("fitforge.cli.shell.interview", return_value=profile),
                patch("fitforge.cli.shell.views.show_stats"),
                patch("fitforge.cli.shell.views.show_plan"),
                contextlib.redirect_stdout(io.StringIO()) as output,
            ):
                shell._create_profile("Recreated")
                self.assertTrue(storage.path_for("Recreated").exists())
                self.assertIn("ابدأ من هنا", output.getvalue())
                self.assertIn("today", output.getvalue())
                self.assertIn("start", output.getvalue())
                self.assertIn("help", output.getvalue())
                self.assertIn("Commands", output.getvalue())
                self.assertIn("ask <question>", output.getvalue())
                self.assertIn("swap <old>", output.getvalue())

    def test_back_returns_to_previous_profile_question_and_keeps_answers(self):
        answers = [
            "1", "25", "180", "back", "back", "back", "back", "Updated Name",
            "2", "25", "180", "90", "80",
            "1", "1", "1", "1", "4", "1", "1",
        ]
        with (
            patch("builtins.input", side_effect=answers),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            profile = interview("Original Name")

        self.assertEqual(profile.name, "Updated Name")
        self.assertEqual(profile.sex, "female")
        self.assertEqual(profile.age, 25)
        self.assertEqual(profile.days_per_week, 4)

    def test_edit_profile_starts_at_first_question_and_supports_back(self):
        old = make_profile()
        answers = ["2", "back", "1", "25", "180", "90", "80", "1", "1", "1", "1", "4", "1", "1"]
        with (
            patch("builtins.input", side_effect=answers),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            edited = interview(old.name, old)

        self.assertEqual(edited.name, old.name)
        self.assertEqual(edited.sex, old.sex)

    def test_back_navigation_can_recreate_a_damaged_save(self):
        shell = Shell()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(storage, "SAVE_DIR", Path(directory)):
                storage.path_for("Damaged User").write_text("{", encoding="utf-8")
                with (
                    patch(
                        "fitforge.cli.shell.interview",
                        side_effect=lambda name, name_is_available: (
                            make_profile(name=name)
                            if name_is_available(name)
                            else self.fail("The damaged profile name should be reusable.")
                        ),
                    ),
                    patch("fitforge.cli.shell.views.show_stats"),
                    patch("fitforge.cli.shell.views.show_plan"),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    shell._create_profile("Damaged User", replace_existing=True)

                self.assertEqual(storage.Account.load("Damaged User").profile.name, "Damaged User")


if __name__ == "__main__":
    unittest.main()