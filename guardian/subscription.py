from datetime import date

from dateutil.relativedelta import relativedelta

from guardian.display import money

# Fixed categories (tuple because they never change)
CATEGORIES = ("video", "music", "sport", "gaming", "apps", "other")
CYCLES = ("monthly", "yearly", "custom")


class Subscription:
    """Base class for any subscription."""

    def __init__(self, name: str, price: float, category: str, start_date: date):
        self.name = name
        self.price = price
        self.category = category
        self.start_date = start_date
        self.cycle = "unknown"

    def monthly_cost(self) -> float:
        """How much this subscription costs per month (each child class decides)."""
        raise NotImplementedError

    def one_cycle(self) -> relativedelta:
        """How long one cycle is: 1 month or 1 year (each child class decides)."""
        raise NotImplementedError

    def yearly_cost(self) -> float:
        return self.monthly_cost() * 12

    def payments_made(self) -> int:
        """How many times we paid since the start date (the first payment is on the start date)."""
        count = 1
        # Keep adding cycles until we reach a renewal that is today or later
        while self.start_date + self.one_cycle() * count < date.today():
            count += 1
        return count

    def renewal_date(self) -> date:
        """The date this cycle ends and the next payment happens."""
        return self.start_date + self.one_cycle() * self.payments_made()

    def days_left(self) -> int:
        """Number of days until the next renewal."""
        return (self.renewal_date() - date.today()).days

    def paid_so_far(self) -> float:
        """Total money paid for this subscription since the start date."""
        return self.price * self.payments_made()

    def cycle_name(self) -> str:
        """The cycle as the user sees it: 'monthly', 'yearly', '18 months'..."""
        return self.cycle

    def to_dict(self) -> dict:
        """Turn the subscription into a dictionary so it can be saved in JSON."""
        return {
            "name": self.name,
            "price": self.price,
            "cycle": self.cycle,
            "category": self.category,
            "start_date": self.start_date.isoformat(),
        }

    def __str__(self):
        return f"{self.name} ({money(self.price)} / {self.cycle_name()})"


class MonthlySubscription(Subscription):
    def __init__(self, name: str, price: float, category: str, start_date: date):
        super().__init__(name, price, category, start_date)
        self.cycle = "monthly"

    def monthly_cost(self) -> float:
        return self.price

    def one_cycle(self) -> relativedelta:
        return relativedelta(months=1)


class YearlySubscription(Subscription):
    def __init__(self, name: str, price: float, category: str, start_date: date):
        super().__init__(name, price, category, start_date)
        self.cycle = "yearly"

    def monthly_cost(self) -> float:
        return self.price / 12

    def one_cycle(self) -> relativedelta:
        return relativedelta(years=1)


class CustomSubscription(Subscription):
    """A subscription that renews every N months (3, 6, 18...)."""

    def __init__(self, name: str, price: float, category: str, start_date: date, months: int):
        super().__init__(name, price, category, start_date)
        self.cycle = "custom"
        self.months = months

    def monthly_cost(self) -> float:
        return self.price / self.months

    def one_cycle(self) -> relativedelta:
        return relativedelta(months=self.months)

    def cycle_name(self) -> str:
        return f"{self.months} months"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["months"] = self.months
        return data


def create_subscription(cycle: str, name: str, price: float, category: str, start_date: date,
                        months: int = None) -> Subscription:
    """Make the right kind of subscription depending on the cycle."""
    if cycle == "monthly":
        return MonthlySubscription(name, price, category, start_date)
    if cycle == "yearly":
        return YearlySubscription(name, price, category, start_date)
    return CustomSubscription(name, price, category, start_date, months)
