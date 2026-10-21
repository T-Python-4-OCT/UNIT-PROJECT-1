"""Small menus used while booking: cinema and movie."""

from cinema.config.branches import BRANCHES
from cinema.config.movies import MOVIES
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
