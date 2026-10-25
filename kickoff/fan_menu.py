import webbrowser
from rich.panel import Panel
from rich.table import Table

from . import booking, holds, standings, storage, ui
from .decorators import log_action, safe_action
from .errors import KickoffError
from .payment import ApplePay, CardPayment, StcPay
from .pricing import seat_category
from .seatmap import draw_stadium


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


def format_left(seconds):
    return f"{seconds // 60}:{seconds % 60:02d}"


def book_match(session, match):
    """Open the stadium of a match, then offer checkout."""
    seat_loop(session, match)
    if not session.cart.is_empty() and ui.confirm("Go to checkout now?"):
        checkout(session)


@safe_action
def book_tickets(session, matches=None):
    upcoming = matches or [m for m in session.matches if m.is_open]
    match = choose_match(session, upcoming, "Book tickets: upcoming matches", "Type the match number to open its stadium (0 = back)")
    if match is not None:
        book_match(session, match)


def seat_loop(session, match):
    while True:
        session.refresh_bookings()
        for seat in session.sync_cart():
            ui.warn(f"Your 5-minute hold on {seat} expired, the seat was released.")
        booked = session.booked_seats(match.id)
        mine, others = holds.seats_for(match.id, session.token)
        draw_stadium(f"{session.match_title(match)}  |  {match.stadium}  |  {match.date} {match.time}",
                     booked, set(mine) | others)
        if mine:
            ui.info("Your seats: " + ", ".join(f"{s} ({format_left(t)} left)" for s, t in sorted(mine.items())))
        command = input("Seat codes (e.g. A3 A4), type again to remove | clear | done > ").strip().lower()
        if command in ("done", "back", ""):
            return
        if command == "clear":
            for seat in mine:
                session.cart.remove(match.id, seat)
                holds.release(match.id, seat, session.token)
            continue
        for code in command.split():
            try:
                booking.toggle_seat(session, match, code)
            except KickoffError as problem:
                ui.error(str(problem))


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
    """List matches; the user can open the details of one and then jump to booking it."""
    match = choose_match(session, matches, heading, "Match number for details (0 = back)")
    if match is None:
        return
    show_details(session, match)
    if match.is_open and ui.confirm("Book tickets for this match?"):
        book_match(session, match)


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
        
@safe_action      
def my_bookings(session):
    phone = session.phone or ui.ask_phone("Your phone (05XXXXXXXX)")
    session.phone = phone
    mine = booking.bookings_of(session, phone)
    if not mine:
        ui.warn("No bookings for this phone number.")
        return
    table = Table(title=f"My bookings ({phone})", header_style="bold white on blue")
    for column in ("Booking", "Match", "Date", "Seats", "Paid (SAR)", "Ticket", "Match status"):
        table.add_column(column)
    for b in mine:
        match = session.get_match(b.match_id)
        ticket = "[green]Confirmed[/green]" if b.is_confirmed else "[red]Cancelled[/red]"
        table.add_row(b.id, session.match_title(match), f"{match.date} {match.time}", ", ".join(b.seats),
                      f"{b.total:.2f}", ticket, match.status.capitalize())
    ui.console.print(table)
    choice = ui.menu("My bookings", {1: "Cancel a booking", 2: "Read an e-ticket file", 3: "My saved e-ticket files", 0: "Back"})
    if choice == 1:
        booking_id = ui.ask_text("Booking ID (like KT-0003)")
        if ui.confirm("Cancel this booking and free the seats?"):
            cancelled = booking.cancel_booking(session, booking_id, phone)
            storage.log(f"Booking {cancelled.id} cancelled")
            ui.ok(f"{cancelled.id} cancelled. {cancelled.total:.2f} SAR will be refunded.")
    elif choice == 2:
        booking_id = ui.ask_text("Booking ID (like KT-0003)").upper()
        if booking_id not in {b.id for b in mine}:
            raise KickoffError("This booking ID is not in your list.")
        ui.console.print(Panel(storage.read_ticket_file(booking_id), title=f"E-ticket {booking_id}"))
    elif choice == 3:
        own = {b.id + ".txt" for b in mine}                      # only the tickets of this phone number
        files = [name for name in storage.list_ticket_files() if name in own]
        ui.info("Your saved files: " + (", ".join(files) if files else "none yet"))

def print_cart(session):
    lines = booking.cart_lines(session)
    if not lines:
        ui.warn("Your cart is empty.")
        return False
    table = Table(title="Your cart", header_style="bold white on blue")
    for column in ("#", "Match", "Seat", "Category", "Price (SAR)"):
        table.add_column(column)
    for number, (match, seat, price) in enumerate(lines, start=1):
        table.add_row(str(number), session.match_title(match), seat, seat_category(seat), str(price))
    ui.console.print(table)
    ui.info(f"[bold]Total: {booking.cart_subtotal(session)} SAR[/bold]  (seats are held for {holds.HOLD_MINUTES} minutes)")
    return True


@safe_action
def cart_menu(session):
    while True:
        for seat in session.sync_cart():
            ui.warn(f"Your hold on {seat} expired, the seat was released.")
        if not print_cart(session):
            return
        choice = ui.menu("Cart", {1: "Checkout", 2: "Remove a seat", 3: "Empty the cart", 0: "Back"})
        if choice == 0:
            return
        if choice == 1:
            checkout(session)
            return
        lines = booking.cart_lines(session)
        if choice == 2:
            number = ui.ask_int("Line number to remove", 1, len(lines))
            match, seat, _ = lines[number - 1]
            session.cart.remove(match.id, seat)
            holds.release(match.id, seat, session.token)
            ui.ok(f"{seat} removed.")
        elif ui.confirm("Remove everything from the cart?"):
            session.empty_cart()
            ui.ok("Cart is empty.")


def ask_payment():
    choice = ui.menu("Payment method (simulation only, never type a real card)",
                     {1: "Mada / Credit card", 2: "Apple Pay", 3: "STC Pay", 0: "Cancel"})
    if choice == 0:
        return None
    if choice == 1:
        while True:
            try:
                return CardPayment(ui.ask_text("Card number (16 digits)"))
            except KickoffError as problem:
                ui.error(str(problem))
    if choice == 2:
        return ApplePay()
    while True:
        try:
            return StcPay(ui.ask_phone("STC Pay phone (05XXXXXXXX)"))
        except KickoffError as problem:
            ui.error(str(problem))


@safe_action
@log_action("Checkout completed")
def checkout(session):
    for seat in session.sync_cart():
        ui.warn(f"Your hold on {seat} expired, the seat was released.")
    if not print_cart(session):
        return False
    name = ui.ask_name("Your full name")
    phone = ui.ask_phone()
    percent = 0
    code = ui.ask_text("Coupon code (press Enter to skip)", allow_empty=True)
    if code:
        try:
            percent = booking.discount_percent(code)
            ui.ok(f"Coupon accepted: {percent}% off.")
        except KickoffError as problem:
            ui.error(str(problem))
    total = round(booking.cart_subtotal(session) * (1 - percent / 100), 2)
    ui.info(f"[bold]Amount to pay: {total:.2f} SAR[/bold]")
    payment = ask_payment()
    if payment is None or not ui.confirm(f"Pay {total:.2f} SAR now?"):
        ui.warn("Checkout cancelled. Your seats stay held until the time runs out.")
        return False
    for b in booking.checkout(session, name, phone, payment, percent):
        ui.console.print(Panel(booking.receipt_text(session, b), title=f"Receipt {b.id}", style="green"))
    ui.ok("Payment done. Your seats are now red for everyone. E-tickets were saved in the 'tickets' folder.")
