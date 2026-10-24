"""Numbers about all bookings: tickets, revenue and the most popular movie."""

from cinema.models.booking import Booking


def count_tickets(bookings: list[Booking], field: str) -> dict:
    """Tickets for each value of a field, e.g. field='movie' -> {'Desert Falcon': 5, ...}."""
    counts = {}
    for booking in bookings:
        key = booking.to_dict()[field]
        counts[key] = counts.get(key, 0) + len(booking.seats)
    return counts


def revenue_by_branch(bookings: list[Booking]) -> dict:
    revenue = {}
    for booking in bookings:
        revenue[booking.branch] = revenue.get(booking.branch, 0) + booking.total
    return revenue


def summary(bookings: list[Booking]) -> dict:
    tickets = sum(len(booking.seats) for booking in bookings)
    revenue = sum(booking.total for booking in bookings)
    movie_counts = count_tickets(bookings, "movie")
    top_movie = max(movie_counts, key=lambda title: movie_counts[title])
    return {
        "bookings": len(bookings),
        "tickets": tickets,
        "customers": len({booking.customer for booking in bookings}),
        "revenue": revenue,
        "average_price": revenue / tickets,
        "top_movie": top_movie,
        "top_movie_tickets": movie_counts[top_movie],
    }


def sort_biggest_first(counts: dict) -> list[tuple]:
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)
