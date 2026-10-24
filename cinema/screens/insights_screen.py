"""Screen for movie recommendations."""

from cinema.config.branches import where_showing
from cinema.config.movies import MOVIES
from cinema.services.recommendations import TOP_PICKS, favourite_genre, recommend_movies
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
