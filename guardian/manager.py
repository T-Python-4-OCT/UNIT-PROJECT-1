"""SubscriptionManager: keeps the list of subscriptions, changes it, and shows it as a table."""
from functools import wraps

from rich.console import Console
from rich.table import Table

from guardian.display import money
from guardian.storage import Storage
from guardian.subscription import Subscription

console = Console()

# Sort options: name shown to the user -> (lambda that gives the sort key, biggest first?)
SORT_OPTIONS = {
    "Days left (soonest first)": (lambda sub: sub.days_left(), False),
    "Monthly cost (highest first)": (lambda sub: sub.monthly_cost(), True),
    "Name (A-Z)": (lambda sub: sub.name.lower(), False),
}


def auto_save(method):
    """Decorator: run the method, then save all subscriptions to the file automatically."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.save()
        return result
    return wrapper


class SubscriptionManager:
    """Keeps the list of subscriptions and works on it."""

    def __init__(self, storage: Storage = None):
        self.storage = storage or Storage()
        self.subscriptions: list[Subscription] = self.storage.load()

    def save(self):
        """Write all subscriptions to the data file."""
        self.storage.save(self.subscriptions)

    @auto_save
    def add(self, subscription: Subscription):
        """Add a new subscription."""
        self.subscriptions.append(subscription)

    @auto_save
    def delete(self, subscription: Subscription):
        """Remove a subscription."""
        self.subscriptions.remove(subscription)

    @auto_save
    def edit(self, subscription: Subscription, field: str, value):
        """Change one field of a subscription, for example edit(netflix, "price", 50)."""
        setattr(subscription, field, value)

    @auto_save
    def replace(self, old: Subscription, new: Subscription):
        """Put a new subscription in the same place as an old one (used when the cycle changes)."""
        index = self.subscriptions.index(old)
        self.subscriptions[index] = new

    def names(self, except_for: Subscription = None) -> list[str]:
        """Names of all subscriptions except one (used so a name can't be taken twice)."""
        return [sub.name for sub in self.subscriptions if sub is not except_for]

    def view_all(self, sort_by: str = "Days left (soonest first)"):
        """Print all subscriptions in a colored table, sorted by one of SORT_OPTIONS."""
        if not self.subscriptions:
            console.print("[yellow]You don't have any subscriptions yet.[/yellow]")
            return

        key, biggest_first = SORT_OPTIONS[sort_by]
        sorted_subs = sorted(self.subscriptions, key=key, reverse=biggest_first)

        table = Table(title=f"Your Subscriptions (sorted by {sort_by.lower()})")
        table.add_column("#", justify="right")
        table.add_column("Name", style="bold")
        # Numbers and dates never wrap; only the name wraps if the window is too narrow
        table.add_column("Price", justify="right", no_wrap=True)
        table.add_column("Per Month", justify="right", no_wrap=True)
        table.add_column("Cycle", no_wrap=True)
        table.add_column("Category")
        table.add_column("Start", no_wrap=True)
        table.add_column("Ends", no_wrap=True)
        table.add_column("Days Left", justify="right", no_wrap=True)
        table.add_column("Paid So Far", justify="right", style="bold magenta", no_wrap=True)

        for number, sub in enumerate(sorted_subs, start=1):
            table.add_row(
                str(number),
                sub.name,
                money(sub.price),
                money(sub.monthly_cost()),
                sub.cycle_name(),
                sub.category,
                str(sub.start_date),
                str(sub.renewal_date()),
                days_left_text(sub.days_left()),
                money(sub.paid_so_far()),
            )

        console.print(table)


def days_left_text(days: int) -> str:
    """Turn days left into colored text: red (10 or less), yellow (30 or less), green."""
    if days < 0:
        return "[red]expired[/red]"
    if days == 0:
        return "[bold red]TODAY[/bold red]"
    if days == 1:
        return "[bold red]TOMORROW[/bold red]"
    if days <= 10:
        return f"[red]{days} days[/red]"
    if days <= 30:
        return f"[yellow]{days} days[/yellow]"
    return f"[green]{days} days[/green]"
