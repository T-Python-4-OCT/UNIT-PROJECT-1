from questionary import Choice
from rich.console import Console

from guardian.manager import SORT_OPTIONS, SubscriptionManager
from guardian.subscription import CATEGORIES, MonthlySubscription, YearlySubscription
from guardian.utils import ask_choice, ask_confirm, ask_price, ask_start_date, ask_text, show_banner

console = Console()
manager = SubscriptionManager()

EXIT = "Exit"
CANCEL = "Cancel"


def add_subscription():
    console.print("\n[bold]Add a new subscription[/bold]")
    name = ask_text("Name: ")
    price = ask_price("Price (SAR): ")

    cycle = ask_choice("Cycle:", ("monthly", "yearly"))
    if cycle is None:
        return

    category = ask_choice("Category:", CATEGORIES)
    if category is None:
        return

    start_date = ask_start_date("Start date (YYYY-MM-DD): ")

    if cycle == "monthly":
        subscription = MonthlySubscription(name, price, category, start_date)
    else:
        subscription = YearlySubscription(name, price, category, start_date)

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
    "Spending report": coming_soon,
    "Mark as used today": coming_soon,
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
