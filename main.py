"""Subscription Guardian: the entry point and the main menu."""
from questionary import Choice
from rich.console import Console

from guardian.display import show_banner
from guardian.manager import SORT_OPTIONS, SubscriptionManager
from guardian.reports import show_spending_report
from guardian.subscription import CATEGORIES, CYCLES, IMPORTANCE_LEVELS, create_subscription
from guardian.validation import GoBack, ask_choice, ask_confirm, ask_months, ask_name, ask_price, ask_start_date

console = Console()
manager = SubscriptionManager()

EXIT = "Exit"
DONE = "Done"


def ask_cycle(message: str) -> tuple[str, int | None]:
    """Ask for the cycle, and for the number of months if it is custom."""
    cycle = ask_choice(message, CYCLES)
    months = ask_months("How many months is one cycle? ") if cycle == "custom" else None
    return cycle, months


def pick_subscription(message: str):
    """Let the user pick one subscription from a list (or Back to return to the menu)."""
    # Show each subscription by its text, but give back the object itself
    choices = [Choice(str(sub), value=sub) for sub in manager.subscriptions]
    return ask_choice(message, choices)


def add_subscription():
    """Menu option 1: ask for every detail and add a new subscription."""
    console.print("\n[bold]Add a new subscription[/bold]")
    name = ask_name("Name: ", manager.names())
    price = ask_price("Price (SAR): ")
    cycle, months = ask_cycle("Cycle:")
    category = ask_choice("Category:", CATEGORIES)
    importance = ask_choice("How important is it to you?", IMPORTANCE_LEVELS)
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

    while True:
        fields = [
            Choice(f"Name ({sub.name})", value="name"),
            Choice(f"Price ({sub.price:g} SAR)", value="price"),
            Choice(f"Cycle ({sub.cycle_name()})", value="cycle"),
            Choice(f"Category ({sub.category})", value="category"),
            Choice(f"Importance ({sub.importance})", value="importance"),
            Choice(f"Start date ({sub.start_date})", value="start_date"),
        ]
        field = ask_choice(f"What do you want to change in {sub.name}?", fields + [DONE], back=False)
        if field is None or field == DONE:
            break

        # Going back while changing a field returns to this list, not to the main menu
        try:
            sub = change_field(sub, field)
        except GoBack:
            continue
        console.print(f"[green]Saved: {sub}[/green]\n")


def change_field(sub, field: str):
    """Ask for the new value of one field, save it, and return the (maybe new) subscription."""
    if field == "name":
        manager.edit(sub, "name", ask_name("New name: ", manager.names(except_for=sub)))
    elif field == "price":
        manager.edit(sub, "price", ask_price("New price (SAR): "))
    elif field == "category":
        manager.edit(sub, "category", ask_choice("New category:", CATEGORIES))
    elif field == "importance":
        manager.edit(sub, "importance", ask_choice("New importance:", IMPORTANCE_LEVELS))
    elif field == "start_date":
        manager.edit(sub, "start_date", ask_start_date("New start date (YYYY-MM-DD): "))
    elif field == "cycle":
        # Each cycle is a different class, so make a new object
        new_cycle, months = ask_cycle("New cycle:")
        new_sub = create_subscription(new_cycle, sub.name, sub.price, sub.category,
                                      sub.start_date, months, sub.importance)
        manager.replace(sub, new_sub)
        return new_sub
    return sub


def delete_subscription():
    """Menu option 5: delete a subscription after asking "Are you sure?"."""
    if not manager.subscriptions:
        console.print("[yellow]You don't have any subscriptions to delete.[/yellow]")
        return

    subscription = pick_subscription("Which subscription do you want to delete?")

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

        choice = ask_choice("What do you want to do?", list(MENU_OPTIONS) + [EXIT], back=False)

        # choice is None when the user presses Ctrl+C
        if choice is None or choice == EXIT:
            console.print("[bold]Goodbye! Keep your money safe.[/bold]")
            break

        # Ctrl+C in the middle of an option cancels it and goes back to the menu
        try:
            MENU_OPTIONS[choice]()
        except GoBack:
            continue  # straight back to the menu, no "Press Enter"
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Cancelled.[/yellow]")

        # Wait so the user can read the result before the screen is cleared
        try:
            input("\nPress Enter to go back to the menu...")
        except (KeyboardInterrupt, EOFError):
            pass


if __name__ == "__main__":
    main()
