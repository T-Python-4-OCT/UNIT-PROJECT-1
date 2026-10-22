"""Small menus used while booking: cinema, movie, experience and showtime."""

from datetime import date, timedelta

from cinema.config.branches import BRANCHES
from cinema.config.movies import MOVIES
from cinema.config.settings import FIRST_SHOW_DAY, LAST_SHOW_DAY, SHOW_TIMES
from cinema.models.hall import Hall
from cinema.models.hall_types import get_halls
from cinema.ui.inputs import ask_menu


def format_date(iso_date: str) -> str:
    """2026-10-21 -> Wed 21 Oct 2026"""
    return date.fromisoformat(iso_date).strftime("%a %d %b %Y")


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


def show_days() -> list[date]:
    """All days from FIRST_SHOW_DAY to LAST_SHOW_DAY."""
    first_day = date.fromisoformat(FIRST_SHOW_DAY)
    last_day = date.fromisoformat(LAST_SHOW_DAY)
    days = []
    day = first_day
    while day <= last_day:
        days.append(day)
        day += timedelta(days=1)
    return days


def choose_show_time() -> tuple[str, str]:
    """Return (date, time)."""
    days = show_days()
    labels = [format_date(day.isoformat()) for day in days]
    day_choice = ask_menu(labels, "Choose a day: ")
    show_date = days[day_choice - 1].isoformat()

    print()
    time_choice = ask_menu(list(SHOW_TIMES), "Choose a showtime: ")
    return show_date, SHOW_TIMES[time_choice - 1]
