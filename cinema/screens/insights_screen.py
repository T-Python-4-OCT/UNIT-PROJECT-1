"""Screens for recommendations and cinema statistics."""

from cinema.config.branches import where_showing
from cinema.config.movies import MOVIES
from cinema.services.recommendations import TOP_PICKS, favourite_genre, recommend_movies
from cinema.services.statistics import count_tickets, revenue_by_branch, sort_biggest_first, summary
from cinema.storage.bookings_file import load_bookings
from cinema.storage.search import find_by_name
from cinema.ui.decorators import pause_after
from cinema.ui.display import clear_screen, print_info, print_title
from cinema.ui.inputs import ask_name


def print_movie_suggestion(movie_id: int) -> None:
    movie = MOVIES[movie_id]
    print(f"  ★ {movie['title']} ({movie['year']}, {movie['genre']})")
    print(f"      Showing at: {', '.join(where_showing(movie_id))}")


@pause_after
def show_recommendations() -> None:
    clear_screen()
    print_title("Recommendations For You")
    name = ask_name()
    history = find_by_name(load_bookings(), name)

    if not history:
        print_info("\nNo bookings yet with this name. Here are our top picks:")
        for movie_id in TOP_PICKS:
            print_movie_suggestion(movie_id)
        return

    print_info(f"\nYou booked {len(history)} time(s). Your favourite genre is: {favourite_genre(history)}")
    print("Movies we think you will enjoy:")
    for movie_id in recommend_movies(history):
        print_movie_suggestion(movie_id)


def print_bar_chart(counts: dict, unit: str) -> None:
    """Simple text chart, biggest first."""
    for name, value in sort_biggest_first(counts):
        print(f"  {name:<30} {'█' * min(int(value), 30)} {value:.0f} {unit}")


@pause_after
def show_statistics() -> None:
    clear_screen()
    print_title("Cinema Statistics")
    bookings = load_bookings()
    if not bookings:
        print_info("No bookings yet. Book a ticket first!")
        return

    numbers = summary(bookings)
    print(f"Total bookings   : {numbers['bookings']}")
    print(f"Tickets sold     : {numbers['tickets']}")
    print(f"Customers        : {numbers['customers']}")
    print(f"Total revenue    : {numbers['revenue']:,.0f} SAR")
    print(f"Avg ticket price : {numbers['average_price']:.1f} SAR")
    print(f"Most popular     : {numbers['top_movie']} ({numbers['top_movie_tickets']} tickets)")

    print("\nTickets per movie:")
    print_bar_chart(count_tickets(bookings, "movie"), "tickets")

    print("\nTickets per experience:")
    print_bar_chart(count_tickets(bookings, "hall"), "tickets")

    print("\nRevenue per cinema:")
    for branch, amount in sort_biggest_first(revenue_by_branch(bookings)):
        print(f"  {branch:<30} {amount:,.0f} SAR")
