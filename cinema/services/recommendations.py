"""Movie recommendations based on the customer's booking history."""

from cinema.config.movies import MOVIES
from cinema.models.booking import Booking

TOP_PICKS = (101, 106, 103)  # shown when the customer has no history


def favourite_genre(bookings: list[Booking]) -> str | None:
    counts = {}
    for booking in bookings:
        counts[booking.genre] = counts.get(booking.genre, 0) + 1
    if not counts:
        return None
    return max(counts, key=lambda genre: counts[genre])


def recommend_movies(history: list[Booking]) -> list[int]:
    """Movies of the favourite genre that the customer did not watch yet."""
    genre = favourite_genre(history)
    watched = {booking.movie for booking in history}  # set of movie titles

    suggestions = []
    for movie_id, movie in MOVIES.items():
        if movie["genre"] == genre and movie["title"] not in watched:
            suggestions.append(movie_id)

    if not suggestions:  # watched everything in this genre -> suggest new genres
        for movie_id, movie in MOVIES.items():
            if movie["title"] not in watched and movie["genre"] != genre:
                suggestions.append(movie_id)
        suggestions = suggestions[:3]
    return suggestions
