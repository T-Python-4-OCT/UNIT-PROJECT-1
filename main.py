"""Subscription Guardian: the entry point and the main menu."""
from questionary import Choice
from rich.console import Console

from guardian.display import show_banner
from guardian.manager import SORT_OPTIONS, SubscriptionManager
from guardian.reports import show_spending_report
from guardian.subscription import CATEGORIES, CYCLES, IMPORTANCE_LEVELS, create_subscription
from guardian.validation import ask_choice, ask_confirm, ask_months, ask_name, ask_price, ask_start_date

console = Console()
manager = SubscriptionManager()

EXIT = "Exit"
CANCEL = "Cancel"
DONE = "Done"


def ask_cycle(message: str) -> tuple[str, int | None] | None:
    """Ask for the cycle, and for the number of months if it is custom (None if Ctrl+C)."""
    cycle = ask_choice(message, CYCLES)
    if cycle is None:
        return None
    months = ask_months("How many months is one cycle? ") if cycle == "custom" else None
    return cycle, months


def pick_subscription(message: str):
    """Let the user pick one subscription from a list (None if they cancel)."""
    # Show each subscription by its text, but give back the object itself
    choices = [Choice(str(sub), value=sub) for sub in manager.subscriptions]
    subscription = ask_choice(message, choices + [CANCEL])
    if subscription == CANCEL:
        return None
    return subscription


def add_subscription():
    """Menu option 1: ask for every detail and add a new subscription."""
    console.print("\n[bold]Add a new subscription[/bold]")
    name = ask_name("Name: ", manager.names())
    price = ask_price("Price (SAR): ")

    answer = ask_cycle("Cycle:")
    if answer is None:
        return
    cycle, months = answer

    category = ask_choice("Category:", CATEGORIES)
    if category is None:
        return

    importance = ask_choice("How important is it to you?", IMPORTANCE_LEVELS)
    if importance is None:
        return

    start_date = ask_start_date("Start date (YYYY-MM-DD): ")

    subscription = create_subscription(cycle, name, price, category, start_date, months, importance)
    manager.add(subscription)
    console.print(f"[green]Added {subscription}[/green]")
    console.print(f"Next renewal: [bold]{subscription.renewal_date()}[/bold] "
                  f"({subscription.days_left()} days left)")


def view_subscriptions():
    """Menu option 2: show all subscriptions in a table, sorted the way the user picks."""
    if not manager.subscriptions:
        manager.view_all()  # prints "no subscriptions yet"
        return

    sort_by = ask_choice("Sort by:", list(SORT_OPTIONS))
    if sort_by is None:
        return
    manager.view_all(sort_by)


def spending_report():
    """Menu option 3: totals, spending by category, and suggestions on what to cancel."""
    show_spending_report(manager.subscriptions)


def edit_subscription():
    """Menu option 4: change any detail of a subscription until the user picks Done."""
    if not manager.subscriptions:
        console.print("[yellow]You don't have any subscriptions to edit.[/yellow]")
        return

    sub = pick_subscription("Which subscription do you want to edit?")
    if sub is None:
        return

    while True:
        fields = [
            Choice(f"Name ({sub.name})", value="name"),
            Choice(f"Price ({sub.price:g} SAR)", value="price"),
            Choice(f"Cycle ({sub.cycle_name()})", value="cycle"),
            Choice(f"Category ({sub.category})", value="category"),
            Choice(f"Importance ({sub.importance})", value="importance"),
            Choice(f"Start date ({sub.start_date})", value="start_date"),
        ]
        field = ask_choice(f"What do you want to change in {sub.name}?", fields + [DONE])
        if field is None or field == DONE:
            break

        if field == "name":
            manager.edit(sub, "name", ask_name("New name: ", manager.names(except_for=sub)))
        elif field == "price":
            manager.edit(sub, "price", ask_price("New price (SAR): "))
        elif field == "category":
            manager.edit(sub, "category", ask_choice("New category:", CATEGORIES) or sub.category)
        elif field == "importance":
            manager.edit(sub, "importance", ask_choice("New importance:", IMPORTANCE_LEVELS) or sub.importance)
        elif field == "start_date":
            manager.edit(sub, "start_date", ask_start_date("New start date (YYYY-MM-DD): "))
        elif field == "cycle":
            answer = ask_cycle("New cycle:")
            if answer:
                # Each cycle is a different class, so make a new object
                new_cycle, months = answer
                new_sub = create_subscription(new_cycle, sub.name, sub.price, sub.category,
                                              sub.start_date, months, sub.importance)
                manager.replace(sub, new_sub)
                sub = new_sub

        console.print(f"[green]Saved: {sub}[/green]\n")


def delete_subscription():
    """Menu option 5: delete a subscription after asking "Are you sure?"."""
    if not manager.subscriptions:
        console.print("[yellow]You don't have any subscriptions to delete.[/yellow]")
        return

    subscription = pick_subscription("Which subscription do you want to delete?")
    if subscription is None:
        return

    if ask_confirm(f'Are you sure you want to delete "{subscription.name}"?'):
        manager.delete(subscription)
        console.print(f"[green]Deleted {subscription.name}.[/green]")
    else:
        console.print("Nothing was deleted.")


# Each menu option and the function it runs
MENU_OPTIONS = {
    "Add subscription": add_subscription,
    "View all subscriptions": view_subscriptions,
    "Spending report": spending_report,
    "Edit subscription": edit_subscription,
    "Delete subscription": delete_subscription,
}


def main():
    """Show the title and the menu again and again until the user picks Exit."""
    while True:
        console.clear()
        show_banner()

        choice = ask_choice("What do you want to do?", list(MENU_OPTIONS) + [EXIT])

        # choice is None when the user presses Ctrl+C
        if choice is None or choice == EXIT:
            console.print("[bold]Goodbye! Keep your money safe.[/bold]")
            break

        # Ctrl+C in the middle of an option cancels it and goes back to the menu
        try:
            MENU_OPTIONS[choice]()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Cancelled.[/yellow]")

        # Wait so the user can read the result before the screen is cleared
        try:
            input("\nPress Enter to go back to the menu...")
        except (KeyboardInterrupt, EOFError):
            pass


if __name__ == "__main__":
    main()
