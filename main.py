
import os
from validation import validate_menu_choice,validate_club_number
from clubs import clubs, team_ids
from football_api import get_club_info, get_club_matches
from design import (
    show_main_menu,
    show_clubs,
    show_favorites,
    show_club_info,
    show_team_selection,
    show_matches,

)

favorites = []

def main_menu():

    while True:

        show_main_menu()
        choice = input("\nEnter your choice: ")

        if not validate_menu_choice(choice, ["0" , "1" , "2" , "3" , "4"]):
            input("\npress Enter to try again...")
            continue

        if choice == "1":

            show_clubs(clubs)

        
            club_number = input("\nEnter club number: ")

            if validate_club_number(club_number, len(clubs)):
                club_number = int(club_number.strip())

                selected_club = clubs[club_number - 1]

                os.system("cls" if os.name == "nt" else "clear")

                print("\n========== CLUB INFORMATION ==========\n")
                selected_club.display_info()


            input("\nPress Enter to return to the main menu...")

        elif choice == "2":

            print("\n========== FAVORITE CLUBS ==========")
            print("1. ⭐ Add Favorite Club")
            print("2. 📋 View Favorite Clubs")
            print("3. ❌ Remove Favorite Club")
            print("0. 🔙 Back to Main Menu")



            favorite_choice = input("\nEnter your choice: ").strip()

            if not validate_menu_choice(favorite_choice, ["0", "1", "2", "3"]):
                input("\nPress Enter to return to the main menu...")
                continue



            if favorite_choice == "1":

                show_clubs(clubs)

                club_number = input("\nEnter club number: ")

                if club_number.isdigit():

                    club_number = int(club_number)

                    if 1 <= club_number <= len(clubs):

                        selected_club = clubs[club_number - 1]

                        if selected_club not in favorites:

                            favorites.append(selected_club)

                            print(
                                f"\n⭐ {selected_club.name} added to favorites!"
                            )

                        else:
                            print("This club is already in your favorites!")

                    else:
                        print("Invalid club number!")

                else:
                    print("Please enter a valid number!")

                input("\nPress Enter to return to the main menu...")

            elif favorite_choice == "2":

                show_favorites(favorites)

                input("\nPress Enter to return to the main menu...")

            elif favorite_choice == "3":

                show_favorites(favorites)

                if favorites:

                    club_number = input(
                        "\nEnter club number to remove: "
                    )

                    if (
                        club_number.isdigit()
                        and 1 <= int(club_number) <= len(favorites)
                    ):

                        removed_club = favorites.pop(
                            int(club_number) - 1
                        )

                        print(
                            f"\n❌ {removed_club.name} removed from favorites!"
                        )

                input("\nPress Enter to return to the main menu...")

            elif favorite_choice == "0":
                continue

            else:
                print("Invalid choice!")

        elif choice == "3":

            print("\n========== CLUB INFORMATION ==========")

            show_team_selection(team_ids)

            club_choice = input("\nEnter club number: ")

            if validate_club_number(club_choice, len(team_ids)):

                team_name = list(team_ids.keys())[
                    int(club_choice.strip()) - 1
                ]

                team_id = team_ids[team_name]

                data = get_club_info(team_id)

                if data:
                    show_club_info(data)

                else:
                    print("Could not load club information.")

            input("\nPress Enter to return to the main menu...")

        elif choice == "4":

            print("\n========== CLUB MATCHES ==========")

            show_team_selection(team_ids)

            club_choice = input("\nEnter club number: ")

            if validate_club_number(club_choice, len(team_ids)):

                team_name = list(team_ids.keys())[
                    int(club_choice.strip()) - 1
    ]

                team_id = team_ids[team_name]

                data = get_club_matches(team_id)

                if data is not None:
                    matches = data.get("matches", [])
                    show_matches(matches)

                else:
                    print("Could not load matches.")

            input("\nPress Enter to return to the main menu...")

        elif choice == "0":
            print("\n👋 Thank you for using Football Hub!")
            break

if __name__ == "__main__":
    main_menu()


                    