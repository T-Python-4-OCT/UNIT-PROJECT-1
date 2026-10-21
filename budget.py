def calculate_daily_budget(budget, days):
    return budget / days


def get_budget_level(daily_budget):
    if daily_budget < 200:
        return "💸 Low Budget"

    elif daily_budget < 500:
        return "💰 Moderate Budget"

    elif daily_budget < 1000:
        return "💵 Comfortable Budget"

    else:
        return "💎 High Budget"


def check_budget(budget, days):
    if budget <= 0:
        print("❌ Budget must be greater than 0.")
        return None

    if days <= 0:
        print("❌ Number of days must be greater than 0.")
        return None

    daily_budget = calculate_daily_budget(
        budget,
        days
    )

    budget_level = get_budget_level(
        daily_budget
    )

    return {
        "budget": budget,
        "days": days,
        "daily_budget": daily_budget,
        "budget_level": budget_level
    }


def show_budget():
    print()
    print("💵 Budget Planner")
    print()

    while True:
        try:
            budget = float(
                input("💰 Enter your budget in SAR: ")
            )

            days = int(
                input("📅 How many days will you travel? ")
            )

            result = check_budget(
                budget,
                days
            )

            if result is not None:
                print()
                print(
                    f"💰 Total Budget: "
                    f"{result['budget']:.2f} SAR"
                )

                print(
                    f"📅 Trip Duration: "
                    f"{result['days']} days"
                )

                print(
                    f"💵 Daily Budget: "
                    f"{result['daily_budget']:.2f} SAR"
                )

                print(
                    f"📊 Budget Level: "
                    f"{result['budget_level']}"
                )

                return result

        except ValueError:
            print(
                "❌ Please enter valid numbers."
            )


if __name__ == "__main__":
    show_budget()