from colorama import Fore, Style, just_fix_windows_console
just_fix_windows_console()
class Club:
    def __init__(self, name, country, stadium, founded, color):
        self.name = name
        self.country = country
        self.stadium = stadium
        self.founded = founded
        self.color = color

    def display_info(self):
        print(f"{getattr(Fore, self.color, Fore.WHITE)}⚽ Club: {self.name}{Style.RESET_ALL}")
        print(f"🌍 Country: {self.country}")
        print(f"🏟️ Stadium: {self.stadium}")
        print(f"📅 Founded: {self.founded}")



al_nassr = Club("Al Nassr", "Saudi Arabia", "Al Awwal Park", 1955, "YELLOW")
al_hilal = Club("Al Hilal", "Saudi Arabia", "Kingdom Arena", 1957, "BLUE")
al_ahli = Club("Al Ahli", "Saudi Arabia", "King Abdullah Sports City", 1937, "GREEN")
al_ittihad = Club("Al Ittihad", "Saudi Arabia", "King Abdullah Sports City", 1927, "YELLOW")

real_madrid = Club("Real Madrid", "Spain", "Santiago Bernabeu", 1902, "WHITE")
barcelona = Club("FC Barcelona", "Spain", "Spotify Camp Nou", 1899, "RED")
liverpool = Club("Liverpool", "England", "Anfield", 1892, "RED")
man_city = Club("Manchester City", "England", "Etihad Stadium", 1880, "CYAN")
man_united = Club("Manchester United", "England", "Old Trafford", 1878, "RED")
juventus = Club("Juventus", "Italy", "Allianz Stadium", 1897, "WHITE")

clubs = [
    al_nassr,
    al_hilal,
    al_ahli,
    al_ittihad,
    real_madrid,
    barcelona,
    liverpool,
    man_city,
    man_united,
    juventus,
]


team_ids = {
    "Real Madrid": 86,
    "FC Barcelona": 81,
    "Liverpool": 64,
    "Manchester City": 65,
    "Manchester United": 66,
    "Juventus": 109,
}