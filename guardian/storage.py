import json
from datetime import date
from pathlib import Path

from rich.console import Console

from guardian.subscription import Subscription, create_subscription

console = Console()

# data/subscriptions.json next to main.py
DEFAULT_FILE = Path(__file__).parent.parent / "data" / "subscriptions.json"


class Storage:
    """Saves and loads the subscriptions from a JSON file."""

    def __init__(self, file_path: Path = DEFAULT_FILE):
        self.file_path = Path(file_path)

    def load(self) -> list[Subscription]:
        """Read the subscriptions from the file (empty list if there is no file or it is broken)."""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return [subscription_from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            console.print(f"[red]The data file {self.file_path.name} is broken, starting with an empty list.[/red]")
            return []

    def save(self, subscriptions: list[Subscription]):
        """Write all the subscriptions to the file."""
        self.file_path.parent.mkdir(exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump([sub.to_dict() for sub in subscriptions], file, indent=4)


def subscription_from_dict(data: dict) -> Subscription:
    """Turn a dictionary from the JSON file back into a Subscription object."""
    return create_subscription(
        cycle=data["cycle"],
        name=data["name"],
        price=float(data["price"]),
        category=data["category"],
        start_date=date.fromisoformat(data["start_date"]),
    )
