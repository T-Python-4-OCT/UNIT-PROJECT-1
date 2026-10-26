"""The Booking class: one booking = one invoice."""

from datetime import date


def make_show_key(branch: str, movie: str, hall: str, show_date: str, show_time: str) -> str:
    """A unique text for one show, e.g. 'VOX Riyadh Park|Interstellar|IMAX|2026-10-21|19:15'."""
    return f"{branch}|{movie}|{hall}|{show_date}|{show_time}"


class Booking:
    def __init__(self, invoice: int, customer: str, branch: str, movie: str, genre: str,
                 hall: str, show_date: str, show_time: str, seats: list[str], total: float, extras: list[dict] | None = None):
        self.invoice = invoice
        self.customer = customer
        self.branch = branch
        self.movie = movie
        self.genre = genre
        self.hall = hall
        self.show_date = show_date
        self.show_time = show_time
        self.seats = seats
        self.total = total
        self.extras = extras if extras is not None else []

    def show_key(self) -> str:
        return make_show_key(self.branch, self.movie, self.hall, self.show_date, self.show_time)

    def show_date_text(self) -> str:
        """2026-10-21 -> Wed 21 Oct 2026"""
        return date.fromisoformat(self.show_date).strftime("%a %d %b %Y")

    def seats_text(self) -> str:
        return ", ".join(self.seats)

    def to_dict(self) -> dict:
        """Convert the object to a dictionary so we can save it in JSON."""
        return {
            "invoice": self.invoice,
            "customer": self.customer,
            "branch": self.branch,
            "movie": self.movie,
            "genre": self.genre,
            "hall": self.hall,
            "show_date": self.show_date,
            "show_time": self.show_time,
            "seats": self.seats,
            "total": self.total,
            "extras": self.extras,
        }

    def ticket_text(self) -> str:
        """The ticket as plain text (used on screen and in the .txt file)."""
        lines = [
            "=" * 44,
            "             VOX CINEMAS TICKET",
            "=" * 44,
            f"Invoice No.   : {self.invoice}",
            f"Customer      : {self.customer}",
            f"Cinema        : {self.branch}",
            f"Movie         : {self.movie}",
            f"Experience    : {self.hall}",
            f"Your showtime : {self.show_date_text()} at {self.show_time}",
            f"Seats ({len(self.seats)})     : {self.seats_text()}",
            "-" * 44,
            f"Tickets       : {self.total - self.extras_total():.2f} SAR",
        ]
        if self.extras:
            lines.append("Food & Drinks:")
            for item in self.extras:
                lines.append(f"  {item['category']} {item['name']} x{item['quantity']} : {item['price'] * item['quantity']} SAR")
            lines.append(f"Extras        : {self.extras_total():.2f} SAR")
        lines.extend([
            f"TOTAL         : {self.total:.2f} SAR",
            "=" * 44,
            "  Please arrive 15 minutes before the show",
        ])
        return "\n".join(lines)

    def extras_total(self) -> float:
        return sum(item["price"] * item["quantity"] for item in self.extras)

    def print_ticket(self) -> None:
        print(self.ticket_text())


def booking_from_dict(data: dict) -> Booking:
    """Create a Booking object from a dictionary loaded from JSON."""
    return Booking(
        invoice=data["invoice"],
        customer=data["customer"],
        branch=data["branch"],
        movie=data["movie"],
        genre=data["genre"],
        hall=data["hall"],
        show_date=data["show_date"],
        show_time=data["show_time"],
        seats=data["seats"],
        total=data["total"],
        extras=data.get("extras", []),
    )
