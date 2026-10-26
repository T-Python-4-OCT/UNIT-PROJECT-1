from colorama import Fore, Style, init

init(autoreset=True)


def show_header():
    print(Fore.CYAN + Style.BRIGHT)
    print("=" * 45)
    print("        ⚽ FOOTBALL HUB ⚽")
    print("=" * 45)
    print(Style.RESET_ALL)


def show_main_menu():

    print(Fore.CYAN + Style.BRIGHT + "\n╔══════════════════════════════════════════════╗")
    print(Fore.YELLOW + "║              ⚽ FOOTBALL HUB ⚽              ║")
    print(Fore.CYAN + "╠══════════════════════════════════════════════╣")

    print(Fore.GREEN   + "║   [1]  🏟️  Browse Clubs                       ║")
    print(Fore.YELLOW  + "║   [2]  ⭐  Favorite Clubs                    ║")
    print(Fore.CYAN    + "║   [3]  ℹ️  Club Information                   ║")
    print(Fore.MAGENTA + "║   [4]  📅  Club Matches                      ║")
    print(Fore.RED     + "║   [0]  🚪  Exit                              ║")

    print(Fore.CYAN + "╚══════════════════════════════════════════════╝")

def show_section(title, emoji="⚽"):
    print(Fore.CYAN + Style.BRIGHT)
    print("\n" + "=" * 45)
    print(f"        {emoji} {title}")
    print("=" * 45)
    print(Style.RESET_ALL)


def show_upcoming_match(home, away, date, status):
    print(Fore.YELLOW + f"\n⏳ {date}")
    print(Fore.WHITE + Style.BRIGHT + f"⚽ {home} VS {away}")
    print(Fore.GREEN + f"📅 Status: {status}")
    print(Fore.CYAN + "-" * 45)



def show_clubs(clubs):
    show_section("BROWSE CLUBS", "🏟️")

    for index, club in enumerate(clubs, start=1):
        print(
            Fore.GREEN + f"{index}. ⚽ " +
            Fore.WHITE + Style.BRIGHT + club.name +
            Fore.YELLOW + f"  🌍 {club.country}"
        )

    print(Fore.CYAN + "-" * 45)

def show_favorites(favorites):
    show_section("FAVORITE CLUBS", "⭐")

    if favorites:
        for index, club in enumerate(favorites, start=1):
            print(
                Fore.YELLOW + f"{index}. ⭐ " +
                Fore.WHITE + Style.BRIGHT + club.name
            )
    else:
        print(Fore.RED + "💔 No favorite clubs yet!")

    print(Fore.CYAN + "-" * 45)


def show_club_info(data):
    show_section("CLUB INFORMATION", "🏟️")

    print(Fore.CYAN + f"⚽ Club: {data.get('name')}")
    print(Fore.YELLOW + f"📅 Founded: {data.get('founded')}")
    print(Fore.GREEN + f"🏟️ Stadium: {data.get('venue')}")
    print(Fore.BLUE + f"🌐 Website: {data.get('website')}")

    coach = data.get("coach")

    if coach:
        print(Fore.MAGENTA + f"👨‍💼 Coach: {coach.get('name')}")
    else:
        print(Fore.RED + "👨‍💼 Coach information not available")

    squad = data.get("squad", [])

    print(Fore.YELLOW + "\n👕 PLAYERS")

    if squad:
        for player in squad[-11:]:
            print(Fore.WHITE + f"⚽ {player.get('name')} - {player.get('position')}")
    else:
        print(Fore.RED + "Players information not available")

    competitions = data.get("runningCompetitions", [])

    print(Fore.YELLOW + "\n🏆 COMPETITIONS")

    if competitions:
        for competition in competitions:
            print(Fore.GREEN + f"🏆 {competition.get('name')}")
    else:
        print(Fore.RED + "Competitions information not available")

def show_team_selection(team_ids):
    show_section("SELECT YOUR CLUB", "⚽")

    emojis = ["👑", "🔵", "🔴", "🔵", "🔴", "⚫"]
    colors = [
        Fore.YELLOW,
        Fore.BLUE,
        Fore.RED,
        Fore.CYAN,
        Fore.RED,
        Fore.WHITE
    ]

    for index, team_name in enumerate(team_ids, start=1):
        emoji = emojis[index - 1]
        color = colors[index - 1]

        print(
            color + f"  [{index}]  {emoji} {team_name}"
        )

    print(Fore.CYAN + "═" * 45)


def show_matches(matches):
    if not matches:
        print("No matches available.")
        return

    for match in matches:
        home = match.get("homeTeam", {}).get("name", "Unknown")
        away = match.get("awayTeam", {}).get("name", "Unknown")
        date = match.get("utcDate", "")[:10]
        status = match.get("status", "Unknown")

        show_upcoming_match(home, away, date, status)