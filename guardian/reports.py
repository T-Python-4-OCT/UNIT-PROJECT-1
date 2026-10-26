"""The spending report: totals, spending by category, and suggestions on what to cancel."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from guardian.display import money
from guardian.subscription import Subscription

console = Console()

# One color for each category bar in the Share column
BAR_COLORS = ("#5c9dff", "#e07ce0", "#f5c542", "#5fd38d", "#ff8c66", "#9be7ff")
BAR_WIDTH = 20


def share_bar(share: float, color: str) -> str:
    """Draw a bar like ██████░░░░ 32% (share is a number from 0 to 1)."""
    filled = round(share * BAR_WIDTH)
    empty = BAR_WIDTH - filled
    return f"[{color}]{'█' * filled}[/][grey35]{'░' * empty}[/] {share * 100:>3.0f}%"


def spending_by_category(subscriptions: list[Subscription]) -> dict[str, float]:
    """Add up the monthly cost of every category: {"video": 61.67, "sport": 250, ...}."""
    totals = {}
    for sub in subscriptions:
        totals[sub.category] = totals.get(sub.category, 0) + sub.monthly_cost()
    return totals


def duplicate_categories(subscriptions: list[Subscription]) -> set[str]:
    """Find the categories that have more than one subscription (using sets)."""
    seen = set()
    duplicates = set()
    for sub in subscriptions:
        if sub.category in seen:
            duplicates.add(sub.category)
        seen.add(sub.category)
    return duplicates


def make_suggestions(subscriptions: list[Subscription]) -> list[str]:
    """Suggest what to cancel: subscriptions that are not important, and repeated categories."""
    suggestions = []

    not_important = [sub for sub in subscriptions if sub.importance == "Not important"]
    for sub in not_important:
        suggestions.append(
            f'"{sub.name}" is not important to you. '
            f"Cancel it and save [bold green]{money(sub.yearly_cost())}/year[/]?"
        )

    for category in sorted(duplicate_categories(subscriptions)):
        same = [sub for sub in subscriptions if sub.category == category]
        names = ", ".join(sub.name for sub in same)
        # Keeping only the cheapest one saves the most
        cheapest = min(same, key=lambda sub: sub.yearly_cost())
        savings = sum(sub.yearly_cost() for sub in same) - cheapest.yearly_cost()
        suggestions.append(
            f"You have {len(same)} {category} subscriptions ({names}). "
            f"Keep only one and save up to [bold green]{money(savings)}/year[/]?"
        )

    if not_important:
        total = sum(sub.yearly_cost() for sub in not_important)
        suggestions.append(
            f"[bold]Cancel everything that is not important and save "
            f"[green]{money(total)}[/green] every year.[/bold]"
        )
    return suggestions


def show_suggestions(subscriptions: list[Subscription]):
    """Print the suggestions in a yellow box (or a green one if there is nothing to cancel)."""
    suggestions = make_suggestions(subscriptions)
    if not suggestions:
        console.print(Panel("Great! Every subscription is important and nothing repeats.",
                            title="Suggestions", border_style="green", expand=False))
        return

    text = "\n".join(f"[yellow]⚠[/yellow] {line}" for line in suggestions)
    console.print(Panel(text, title="Suggestions: what to cancel?", border_style="yellow", padding=(0, 1)))


def show_spending_report(subscriptions: list[Subscription]):
    """Print the totals, a table by category with a share bar for each one, and suggestions."""
    if not subscriptions:
        console.print("[yellow]You don't have any subscriptions yet.[/yellow]")
        return

    monthly_total = sum(sub.monthly_cost() for sub in subscriptions)
    yearly_total = monthly_total * 12
    paid_total = sum(sub.paid_so_far() for sub in subscriptions)

    console.print(Panel(
        f"Per month:    [bold #5c9dff]{money(monthly_total)}[/]\n"
        f"Per year:     [bold #5c9dff]{money(yearly_total)}[/]\n"
        f"Paid so far:  [bold magenta]{money(paid_total)}[/]",
        title="Spending Report",
        border_style="#5c9dff",
        expand=False,
        padding=(0, 2),
    ))

    totals = spending_by_category(subscriptions)
    # Biggest category first
    sorted_totals = sorted(totals.items(), key=lambda item: item[1], reverse=True)

    table = Table(title="By Category")
    table.add_column("Category", style="bold")
    table.add_column("Subscriptions", justify="right")
    table.add_column("Per Month", justify="right")
    table.add_column("Per Year", justify="right")
    table.add_column("Share")

    for (category, amount), color in zip(sorted_totals, BAR_COLORS):
        count = len([sub for sub in subscriptions if sub.category == category])
        share = amount / monthly_total
        table.add_row(category, str(count), money(amount), money(amount * 12), share_bar(share, color))

    console.print(table)
    console.print()
    show_suggestions(subscriptions)
