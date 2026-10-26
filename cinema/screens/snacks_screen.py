"""Optional snacks and drinks during Step 7. Prices are example SAR prices."""

from cinema.ui.display import print_info
from cinema.ui.inputs import ask_menu, ask_yes_no

# Name and price for each size, in SAR.
SIZES = [("Small", 10), ("Medium", 15), ("Large", 20)]
DRINKS = [("Small", 8), ("Medium", 12), ("Large", 16)]
SNACKS = [("Chocolate", 7), ("Hot dog", 18), ("Nachos", 16),
          ("Candy", 6), ("Nuts", 9)]


def choose_quantity(seat_count: int) -> int:
    """Enter uses one item for every booked seat; numbers select 1..seat_count."""
    while True:
        text = input(f"Quantity (1-{seat_count}, Enter = {seat_count} seats): ").strip()
        if not text:
            return seat_count
        if not text.isdigit() or not 1 <= int(text) <= seat_count:
            print_info(f"Please enter a number from 1 to {seat_count}, or press Enter.")
            continue
        return int(text)


def choose_extras(seat_count: int) -> list[dict]:
    """Pick any of three categories, maximum one choice per category."""
    if not ask_yes_no("Add popcorn, a drink or a snack to your booking?"):
        return []

    extras = []
    remaining = ["Popcorn", "Drink", "Snack"]
    while remaining:
        print("\nFood & drinks (prices in SAR):")
        option = ask_menu(remaining + ["Done adding items"])
        if option == len(remaining) + 1:
            break
        category = remaining.pop(option - 1)
        if category == "Popcorn":
            choices = SIZES
        elif category == "Drink":
            choices = DRINKS
        else:
            choices = SNACKS
        print(f"\n{category} options:")
        choice = ask_menu([f"{name} - {price} SAR" for name, price in choices])
        name, price = choices[choice - 1]
        quantity = choose_quantity(seat_count)
        extras.append({"category": category, "name": name,
                       "price": price, "quantity": quantity})
        print_info(f"Added: {quantity} x {category} {name} = {quantity * price} SAR")
        if remaining and not ask_yes_no("Add something from another category?"):
            break
    return extras


def extras_total(extras: list[dict]) -> float:
    return sum(item["price"] * item["quantity"] for item in extras)


def print_extras(extras: list[dict]) -> None:
    for item in extras:
        name = f"{item['category']} {item['name']}"
        print(f"  {name:<23} {item['quantity']} x {item['price']:>3} = {item['quantity'] * item['price']:>4} SAR")
