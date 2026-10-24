from kickoff import fan_menu, holds, ui
from kickoff.errors import KickoffError
from kickoff.session import Session

try:
    session = Session()
except KickoffError as problem:             
    ui.error(str(problem))
    raise SystemExit(1)
actions_done = 0          

ui.console.print("[bold cyan]KICKOFF TICKETS[/bold cyan]  -  Roshn Saudi League 2026-27")

MAIN_OPTIONS = {
    2: "League standings",
    3: "Matches",
    6: "Team profiles and logos",
    0: "Exit",
}

ACTIONS = {
    2: fan_menu.standings_menu,
    3: fan_menu.matches_menu,
    6: fan_menu.team_profile,
}

try:
    while True:
        choice = ui.menu("MAIN MENU", MAIN_OPTIONS)
        if choice == 0:
            break
        ACTIONS[choice](session)
        actions_done += 1
except (KeyboardInterrupt, EOFError):
    print()
finally:
    holds.release_all(session.token)         # always free my temporary seat holds

ui.ok("Thank you for using KickOff Tickets. See you at the stadium!")
ui.info(f"This visit: {actions_done} menu actions, {ui.errors_shown} input mistakes.")