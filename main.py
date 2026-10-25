from questionary import Choice
from rich.console import Console

from guardian.manager import SORT_OPTIONS, SubscriptionManager
from guardian.reports import show_spending_report
from guardian.display import show_banner
from guardian.subscription import CATEGORIES, CYCLES, create_subscription
from guardian.validation import ask_choice, ask_confirm, ask_name, ask_price, ask_start_date

console = Console()
manager = SubscriptionManager()

EXIT = "Exit"
CANCEL = "Cancel"
DONE = "Done"


def other_names(subscription=None) -> list[str]:
    """Names of all subscriptions except the given one (so a name can't be used twice)."""
    return [sub.name for sub in manager.subscriptions if sub is not subscription]


def add_subscription():
    console.print("\n[bold]Add a new subscription[/bold]")
    name = ask_name("Name: ", other_names())
    price = ask_price("Price (SAR): ")

    cycle = ask_choice("Cycle:", CYCLES)
    if cycle is None:
        return

    category = ask_choice("Category:", CATEGORIES)
    if category is None:
        return

    start_date = ask_start_date("Start date (YYYY-MM-DD): ")

    subscription = create_subscription(cycle, name, price, category, start_date)
    manager.add(subscription)
    console.print(f"[green]Added {subscription}[/green]")
    console.print(f"Next renewal: [bold]{subscription.renewal_date()}[/bold] "
                  f"({subscription.days_left()} days left)")


def view_subscriptions():
    if not manager.subscriptions:
        manager.view_all()  # prints "no subscriptions yet"
        return

    sort_by = ask_choice("Sort by:", list(SORT_OPTIONS))
    if sort_by is None:
        return
    manager.view_all(sort_by)


def spending_report():
    show_spending_report(manager.subscriptions)


def edit_subscription():
    if not manager.subscriptions:
        console.print("[yellow]You don't have any subscriptions to edit.[/yellow]")
        return

    choices = [Choice(str(sub), value=sub) for sub in manager.subscriptions]
    sub = ask_choice("Which subscription do you want to edit?", choices + [CANCEL])
    if sub is None or sub == CANCEL:
        return

    # Keep editing until the user picks "Done"
    while True:
        fields = [
            Choice(f"Name ({sub.name})", value="name"),
            Choice(f"Price ({sub.price:g} SAR)", value="price"),
            Choice(f"Cycle ({sub.cycle})", value="cycle"),
            Choice(f"Category ({sub.category})", value="category"),
            Choice(f"Start date ({sub.start_date})", value="start_date"),
        ]
        field = ask_choice(f"What do you want to change in {sub.name}?", fields + [DONE])
        if field is None or field == DONE:
            break

        if field == "name":
            sub.name = ask_name("New name: ", other_names(sub))
        elif field == "price":
            sub.price = ask_price("New price (SAR): ")
        elif field == "category":
            sub.category = ask_choice("New category:", CATEGORIES) or sub.category
        elif field == "start_date":
            sub.start_date = ask_start_date("New start date (YYYY-MM-DD): ")
        elif field == "cycle":
            new_cycle = ask_choice("New cycle:", CYCLES)
            if new_cycle and new_cycle != sub.cycle:
                # Monthly and yearly are different classes, so make a new object
                new_sub = create_subscription(new_cycle, sub.name, sub.price, sub.category, sub.start_date)
                manager.replace(sub, new_sub)
                sub = new_sub

        manager.save()
        console.print(f"[green]Saved: {sub}[/green]\n")


def delete_subscription():
    if not manager.subscriptions:
        console.print("[yellow]You don't have any subscriptions to delete.[/yellow]")
        return

    # Show each subscription by its text, but give back the object itself
    choices = [Choice(str(sub), value=sub) for sub in manager.subscriptions]
    subscription = ask_choice("Which subscription do you want to delete?", choices + [CANCEL])
    if subscription is None or subscription == CANCEL:
        return

    if ask_confirm(f'Are you sure you want to delete "{subscription.name}"?'):
        manager.delete(subscription)
        console.print(f"[green]Deleted {subscription.name}.[/green]")
    else:
        console.print("Nothing was deleted.")


def coming_soon():
    console.print("[yellow]Coming soon...[/yellow]")


# Each menu option and the function it runs
MENU_OPTIONS = {
    "Add subscription": add_subscription,
    "View all subscriptions": view_subscriptions,
    "Spending report": spending_report,
    "Edit subscription": edit_subscription,
    "Suggestions: what to cancel?": coming_soon,
    "Delete subscription": delete_subscription,
}


def main():
    while True:
        console.clear()
        show_banner()

        choice = ask_choice("What do you want to do?", list(MENU_OPTIONS) + [EXIT])

        # choice is None when the user presses Ctrl+C
        if choice is None or choice == EXIT:
            console.print("[bold]Goodbye! Keep your money safe.[/bold]")
            break

        MENU_OPTIONS[choice]()

        # Wait so the user can read the result before the screen is cleared
        input("\nPress Enter to go back to the menu...")


if __name__ == "__main__":
    main()
