from kickoff import fan_menu, holds, ui
from kickoff.errors import KickoffError
from kickoff.session import Session

try:
    session = Session()
except KickoffError as problem:             
    ui.error(str(problem))
    raise SystemExit(1)
actions_done = 0          # a global variable (top level): how many menu choices were used

ui.console.print("[bold cyan]KICKOFF TICKETS[/bold cyan]  -  Roshn Saudi League 2026-2027")

MAIN_OPTIONS = {
    1: "Book tickets",
    2: "League standings",
    3: "Matches",
    4: "My bookings",
    5: "My cart and checkout",
    6: "Team profiles and logos",
    0: "Exit",
}

ACTIONS = {
    1: fan_menu.book_tickets,
    2: fan_menu.standings_menu,
    3: fan_menu.matches_menu,
    4: fan_menu.my_bookings,
    5: fan_menu.cart_menu,
    6: fan_menu.team_profile,
}

try:
    while True:
        seats_in_cart = sum(len(seats) for seats in session.cart.items().values())
        options = dict(MAIN_OPTIONS)
        options[5] = f"My cart and checkout ({seats_in_cart} seats)"
        choice = ui.menu("MAIN MENU", options)
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