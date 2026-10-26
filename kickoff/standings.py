from .models import Team


def table(teams: dict[str, Team]) -> list[Team]:
    return sorted(teams.values(), key=lambda t: (-t.points, -t.goal_diff, -t.gf))


def positions(teams: dict[str, Team]) -> dict[str, int]:
    return {team.team_id: index for index, team in enumerate(table(teams), start=1)}