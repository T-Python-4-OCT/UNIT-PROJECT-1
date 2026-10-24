import webbrowser
from rich.panel import Panel
from rich.table import Table

from . import standings, ui
from .decorators import safe_action


def pick_team(session):
    teams = sorted(session.teams.values(), key=lambda t: t.name_en)
    table = Table(header_style="bold white on blue")
    for column in ("#", "Team", "#", "Team"):
        table.add_column(column)
    half = (len(teams) + 1) // 2
    for i in range(half):
        left = teams[i]
        right = teams[i + half] if i + half < len(teams) else None
        table.add_row(str(i + 1), left.name_en,
                      str(i + half + 1) if right else "", right.name_en if right else "")
    ui.console.print(table)
    number = ui.ask_int("Team number", 1, len(teams))
    return teams[number - 1]


def choose_match(session, matches, heading, prompt="Match number (0 = back)"):
    """Show a numbered table and return the match the user picked, or None."""
    if not matches:
        ui.warn("No matches found.")
        return None
    matches = session.sorted_matches(matches)
    ui.matches_table(session, matches, heading)
    number = ui.ask_int(prompt, 0, len(matches))
    return matches[number - 1] if number else None



@safe_action
def standings_menu(session):
    while True:
        choice = ui.menu("League standings", {1: "Full table", 2: "Top 5", 3: "Relegation zone (bottom 3)",
                                              0: "Back"})
        if choice == 0:
            return
        rows = [(team, pos) for pos, team in enumerate(standings.table(session.teams), start=1)]
        if choice == 1:
            ui.standings_table(session, rows)
        elif choice == 2:
            ui.standings_table(session, rows[:5], heading="Top 5")
        else:
            ui.standings_table(session, rows[-3:], heading="Relegation zone")



def show_details(session, match):
    ranking = standings.positions(session.teams)
    home, away = session.teams[match.home_id], session.teams[match.away_id]
    lines = [
        f"[bold]{session.match_title(match)}[/bold]",
        f"Date: {match.date}   Time: {match.time}",
        f"Stadium: {match.stadium}, {match.city}",
        f"Table position: {home.name_en} #{ranking[home.team_id]} ({home.points} pts)  |  "
        f"{away.name_en} #{ranking[away.team_id]} ({away.points} pts)",
    ]
    if match.status == "finished":
        lines.append(f"[green]Final score: {match.home_goals} - {match.away_goals}[/green]")
    ui.console.print(Panel("\n".join(lines), title="Match details"))


def list_and_open(session, matches, heading):
    """List matches; the user can open the details of one."""
    match = choose_match(session, matches, heading, "Match number for details (0 = back)")
    if match is None:
        return
    show_details(session, match)


@safe_action
def matches_menu(session):
    choice = ui.menu("Matches", {1: "Upcoming matches", 2: "Finished results", 3: "By team", 4: "By date",
                                 0: "Back"})
    if choice == 1:
        list_and_open(session, [m for m in session.matches if m.is_open], "Upcoming matches")
    elif choice == 2:
        list_and_open(session, [m for m in session.matches if m.status == "finished"], "Finished results")
    elif choice == 3:
        team = pick_team(session)
        list_and_open(session, [m for m in session.matches if m.involves(team.team_id)], team.name_en)
    elif choice == 4:
        day = ui.ask_date()
        list_and_open(session, [m for m in session.matches if m.date == day], f"Matches on {day}")


@safe_action
def team_profile(session):
    team = pick_team(session)
    position = standings.positions(session.teams)[team.team_id]
    ui.console.print(Panel(
        f"[bold]{team.name_en}[/bold]\n"
        f"City: {team.city}\n"
        f"Table position: #{position}   Points: {team.points}\n"
        f"Played {team.played}  Won {team.won}  Drawn {team.drawn}  Lost {team.lost}\n"
        f"Goals: {team.gf} for, {team.ga} against ({team.goal_diff:+d})\n"
        f"Logo: {team.logo}", title="Team profile"))
    list_and_open(session, [m for m in session.matches if m.involves(team.team_id) and m.is_open],
                  f"Upcoming matches of {team.name_en}")
    if ui.confirm("Open the team logo in your browser?"):
        webbrowser.open(team.logo)