"""Small menus used while booking: cinema, movie, experience and showtime."""

from datetime import date, datetime, timedelta

from cinema.config.branches import BRANCHES
from cinema.config.movies import MOVIES
from cinema.config.settings import SHOW_DAYS_AHEAD, SHOW_TIMES
from cinema.models.hall import Hall
from cinema.models.hall_types import get_halls
from cinema.ui.display import print_error
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
    """Seven calendar days starting today; skip today if all shows have started."""
    days = []
    for offset in range(SHOW_DAYS_AHEAD):
        day = date.today() + timedelta(days=offset)
        if available_times(day.isoformat()):
            days.append(day)
    return days


def available_times(show_date: str) -> list[str]:
    """For today, hide the showtimes that already started."""
    if show_date < date.today().isoformat():
        return []
    if show_date != date.today().isoformat():
        return list(SHOW_TIMES)
    now = datetime.now().strftime("%H:%M")
    return [time for time in SHOW_TIMES if time > now]


def choose_show_time() -> tuple[str, str] | None:
    """Return (date, time), or None if there are no show days left."""
    days = show_days()
    if not days:
        return None

    while True:
        labels = [format_date(day.isoformat()) for day in days]
        day_choice = ask_menu(labels, "Choose a day: ")
        show_date = days[day_choice - 1].isoformat()

        times = available_times(show_date)
        if not times:
            print_error("No more shows today. Please choose another day.")
            continue

        print()
        time_choice = ask_menu(times, "Choose a showtime: ")
        return show_date, times[time_choice - 1]
