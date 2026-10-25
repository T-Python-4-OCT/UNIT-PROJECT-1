from datetime import date

from rich.console import Console
from rich.table import Table

from guardian.storage import Storage
from guardian.subscription import Subscription
from guardian.utils import money

console = Console()

# Sort options: name shown to the user -> (lambda that gives the sort key, biggest first?)
SORT_OPTIONS = {
    "Days left (soonest first)": (lambda sub: sub.days_left(), False),
    "Monthly cost (highest first)": (lambda sub: sub.monthly_cost(), True),
    "Name (A-Z)": (lambda sub: sub.name.lower(), False),
}


class SubscriptionManager:
    """Keeps the list of subscriptions and works on it."""

    def __init__(self, storage: Storage = None):
        self.storage = storage or Storage()
        self.subscriptions: list[Subscription] = self.storage.load()

    def save(self):
        self.storage.save(self.subscriptions)

    def add(self, subscription: Subscription):
        self.subscriptions.append(subscription)
        self.save()

    def delete(self, subscription: Subscription):
        self.subscriptions.remove(subscription)
        self.save()

    def mark_used_today(self, used: list[Subscription]):
        """Set today as the last used date for every subscription in the list."""
        for subscription in used:
            subscription.last_used = date.today()
        self.save()

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
        table.add_column("Price", justify="right")
        table.add_column("/Month", justify="right")
        table.add_column("Cycle")
        table.add_column("Category")
        table.add_column("Start")
        table.add_column("Ends")
        table.add_column("Days Left", justify="right")
        table.add_column("Paid So Far", justify="right", style="bold magenta")

        for number, sub in enumerate(sorted_subs, start=1):
            table.add_row(
                str(number),
                sub.name,
                money(sub.price),
                money(sub.monthly_cost()),
                sub.cycle,
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
