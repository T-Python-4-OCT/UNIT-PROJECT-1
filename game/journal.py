# يسجل الأدلة التي اكتشفها اللاعب

# Tracks evidence, solved puzzles, and discoveries.
# Journal data and translations are stored in JSON files.

import json
from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from game.localization import Localization
from ui.effects import console


DATA_DIR = Path(__file__).parent / "data"
JOURNAL_FILE = DATA_DIR / "journal.json"
JOURNAL_AR_FILE = DATA_DIR / "journal_ar.json"

FOREST_GREEN = "#2F5249"
ANTIQUE_GOLD = "#C5A46D"
SOFT_GREEN = "#A3B18A"
MUTED_GRAY = "#858585"


def load_journal_data(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


class Journal:
    def __init__(self, loc=None):
        self.loc = loc if loc is not None else Localization("en")

        self.data = load_journal_data(JOURNAL_FILE)
        self.arabic_data = load_journal_data(JOURNAL_AR_FILE)

        self.connections = self.data["connections"]

        self.evidence = []
        self.solved_puzzles = []
        self.discoveries = []

    def show_text(self, english, arabic):
        text = arabic if self.loc.language == "ar" else english
        return self.loc.format_arabic(text)

    def translate_evidence(self, evidence):
        if self.loc.language == "ar":
            text = self.arabic_data["evidence"].get(
                evidence, evidence
            )
        else:
            text = evidence

        return self.loc.format_arabic(text)

    def discovery_text(self, discovery_id, field):
        if self.loc.language == "ar":
            translation = self.arabic_data["connections"].get(
                discovery_id, {}
            )
            text = translation.get(
                field,
                self.connections[discovery_id][field]
            )
        else:
            text = self.connections[discovery_id][field]

        return self.loc.format_arabic(text)

    def add_evidence(self, evidence):
        if not evidence or evidence in self.evidence:
            return False

        # Preserve English evidence IDs for connection checks.
        self.evidence.append(evidence)

        label = self.show_text(
            "Evidence added to your journal:",
            "تمت إضافة دليل إلى دفتر الرحلة:"
        )

        console.print(
            Panel(
                Text(
                    f"{label}\n{self.translate_evidence(evidence)}",
                    style=SOFT_GREEN,
                ),
                title="📜 ✦ EVIDENCE ✦",
                border_style=FOREST_GREEN,
                padding=(0, 2),
                expand=False,
            )
        )

        self.check_connections()
        return True

    def record_solved_puzzle(self, puzzle_id):
        puzzle_id = str(puzzle_id)

        if puzzle_id in self.solved_puzzles:
            return False

        self.solved_puzzles.append(puzzle_id)
        return True

    def check_connections(self):
        for connection_id, connection in self.connections.items():
            if connection_id in self.discoveries:
                continue

            if all(
                clue in self.evidence
                for clue in connection["requires"]
            ):
                self.discoveries.append(connection_id)

                label = self.show_text(
                    "NEW DISCOVERY:",
                    "اكتشاف جديد:"
                )

                title = self.discovery_text(connection_id, "title")
                description = self.discovery_text(
                    connection_id, "description"
                )

                content = Group(
                    Text(f"✨ {label}", style=ANTIQUE_GOLD),
                    Text(title, style=ANTIQUE_GOLD),
                    Text(description, style=SOFT_GREEN),
                )

                console.print(
                    Panel(
                        content,
                        title="🔮 ✦ FOREST MEMORY ✦",
                        border_style=ANTIQUE_GOLD,
                        padding=(1, 2),
                        expand=False,
                    )
                )

    def display(self):
        title = self.show_text(
            "YOUR JOURNAL",
            "دفتر رحلتك"
        )

        console.print()
        console.print(
            Panel(
                Text(
                    f"📜 ✦ {title} ✦",
                    style=f"bold {ANTIQUE_GOLD}",
                ),
                border_style=FOREST_GREEN,
                padding=(0, 2),
                expand=False,
            )
        )

        # Discovered evidence
        evidence_lines = Text()

        if self.evidence:
            for index, evidence in enumerate(self.evidence, start=1):
                evidence_lines.append(
                    f"{index}. {self.translate_evidence(evidence)}\n",
                    style=SOFT_GREEN,
                )
        else:
            evidence_lines.append(
                self.show_text(
                    "No evidence discovered yet.",
                    "لم تكتشف أي أدلة بعد."
                ),
                style=MUTED_GRAY,
            )

        evidence_title = self.show_text(
            "DISCOVERED EVIDENCE",
            "الأدلة المكتشفة"
        )

        console.print(
            Panel(
                evidence_lines,
                title=f"📜 {evidence_title}",
                border_style=FOREST_GREEN,
                padding=(0, 2),
                expand=False,
            )
        )

        # Solved puzzles
        puzzle_lines = Text()

        puzzle_names = (
            self.arabic_data["puzzle_names"]
            if self.loc.language == "ar"
            else self.data["puzzle_names"]
        )

        if self.solved_puzzles:
            for puzzle_id in self.solved_puzzles:
                name = puzzle_names.get(
                    str(puzzle_id),
                    "Unknown Puzzle"
                )

                puzzle_lines.append(
                    f"🔮 {self.loc.format_arabic(name)}\n",
                    style=ANTIQUE_GOLD,
                )
        else:
            puzzle_lines.append(
                self.show_text(
                    "No puzzles solved yet.",
                    "لم تحل أي ألغاز بعد."
                ),
                style=MUTED_GRAY,
            )

        puzzles_title = self.show_text(
            "SOLVED PUZZLES",
            "الألغاز المحلولة"
        )

        console.print(
            Panel(
                puzzle_lines,
                title=f"🔮 {puzzles_title}",
                border_style=ANTIQUE_GOLD,
                padding=(0, 2),
                expand=False,
            )
        )

        # Discoveries
        discovery_lines = Text()

        if self.discoveries:
            for discovery_id in self.discoveries:
                if discovery_id in self.connections:
                    name = self.discovery_text(
                        discovery_id, "title"
                    )

                    discovery_lines.append(
                        f"✨ {name}\n",
                        style=ANTIQUE_GOLD,
                    )
        else:
            discovery_lines.append(
                self.show_text(
                    "No discoveries unlocked yet.",
                    "لم تفتح أي اكتشافات بعد."
                ),
                style=MUTED_GRAY,
            )

        discoveries_title = self.show_text(
            "DISCOVERIES",
            "الاكتشافات"
        )

        console.print(
            Panel(
                discovery_lines,
                title=f"✨ {discoveries_title}",
                border_style=FOREST_GREEN,
                padding=(0, 2),
                expand=False,
            )
        )