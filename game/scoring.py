from rich.panel import Panel
from rich.table import Table
from rich.progress_bar import ProgressBar
from rich.console import Group
from rich.text import Text

from game.localization import Localization
from ui.effects import console


FOREST_GREEN = "#2F5249"
ANTIQUE_GOLD = "#C5A46D"
SOFT_GREEN = "#A3B18A"


class Scoring:
    MAX_SCORES = {
        "puzzles": 400,
        "evidence": 250,
        "decisions": 200,
        "secrets": 150,
    }

    CATEGORY_NAMES = {
        "puzzles": "الألغاز",
        "evidence": "الأدلة",
        "decisions": "القرارات",
        "secrets": "الأسرار",
    }

    CATEGORY_ICONS = {
        "puzzles": "🔮",
        "evidence": "📜",
        "decisions": "⚖️",
        "secrets": "✨",
    }

    PUZZLE_BASE_POINTS = 100
    WRONG_ANSWER_PENALTY = 20
    HINT_PENALTY = 10
    MIN_PUZZLE_POINTS = 30

    def __init__(self, loc=None):
        self.loc = loc if loc is not None else Localization("en")

        self.scores = {
            category: 0
            for category in self.MAX_SCORES
        }
        self.rewarded_actions = set()

    @classmethod
    def calculate_puzzle_reward(cls, wrong_attempts=0, hint_used=False):
        wrong_attempts = max(0, int(wrong_attempts))

        points = cls.PUZZLE_BASE_POINTS
        points -= wrong_attempts * cls.WRONG_ANSWER_PENALTY

        if hint_used:
            points -= cls.HINT_PENALTY

        return max(cls.MIN_PUZZLE_POINTS, points)

    def add_points(self, category, action_id, points):
        if category not in self.scores:
            return False

        reward_key = f"{category}:{action_id}"

        if reward_key in self.rewarded_actions:
            return False

        if not isinstance(points, int) or points <= 0:
            return False

        maximum = self.MAX_SCORES[category]
        remaining = maximum - self.scores[category]

        if remaining <= 0:
            return False

        awarded = min(points, remaining)

        self.scores[category] += awarded
        self.rewarded_actions.add(reward_key)

        return True

    def get_category_score(self, category):
        return self.scores.get(category, 0)

    def get_total(self):
        return sum(self.scores.values())

    def get_maximum_total(self):
        return sum(self.MAX_SCORES.values())

    def display_score(self):
        title = (
            "🏆 نقاط المستكشف"
            if self.loc.language == "ar"
            else "🏆 EXPLORER SCORE"
        )

        table = Table(
            show_header=False,
            show_edge=False,
            box=None,
            padding=(0, 2),
        )

        table.add_column(style=SOFT_GREEN)
        table.add_column(style=ANTIQUE_GOLD, justify="right")

        for category, score in self.scores.items():
            maximum = self.MAX_SCORES[category]

            name = (
                self.CATEGORY_NAMES[category]
                if self.loc.language == "ar"
                else category.title()
            )

            label = (
                f"{self.CATEGORY_ICONS[category]} "
                f"{self.loc.format_arabic(name)}"
            )

            table.add_row(label, f"{score}/{maximum}")

        total = self.get_total()
        maximum_total = self.get_maximum_total()

        total_label = (
            "المجموع"
            if self.loc.language == "ar"
            else "TOTAL"
        )

        total_text = Text()
        total_text.append(
            f"\n{self.loc.format_arabic(total_label)}: ",
            style=SOFT_GREEN,
        )
        total_text.append(
            f"{total}/{maximum_total}",
            style=f"bold {ANTIQUE_GOLD}",
        )

        progress = ProgressBar(
            total=maximum_total,
            completed=total,
            width=35,
            complete_style=SOFT_GREEN,
            finished_style=ANTIQUE_GOLD,
        )

        console.print()
        console.print(
            Panel(
                Group(table, total_text, progress),
                title=self.loc.format_arabic(title),
                border_style=FOREST_GREEN,
                padding=(1, 2),
                expand=False,
            )
        )