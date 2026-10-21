"""Small menus used while booking: cinema, movie and experience."""

from cinema.config.branches import BRANCHES
from cinema.config.movies import MOVIES
from cinema.models.hall import Hall
from cinema.models.hall_types import get_halls
from cinema.ui.inputs import ask_menu


def choose_branch() -> str:
    branch_names = list(BRANCHES.keys())
    choice = ask_menu(branch_names, "Choose a cinema: ")
    return branch_names[choice - 1]


def choose_movie(branch: str) -> dict:
    movie_ids = BRANCHES[branch]
    options = []
    for movie_id in movie_ids:
        movie = MOVIES[movie_id]
        options.append(f"{movie['title']:<30} {movie['year']}   {movie['genre']}")
    choice = ask_menu(options, "Choose a movie: ")
    return MOVIES[movie_ids[choice - 1]]


def choose_hall() -> Hall:
    halls = get_halls()
    options = []
    for hall in halls:
        options.append(f"{hall.name:<9} {hall.capacity()} seats - {hall.description}\n"
                       f"              {hall.price_info()}")
    choice = ask_menu(options, "Choose an experience: ")
    return halls[choice - 1]
