def validate_menu_choice(choice, valid_choices):

    choice = choice.strip()

    if not choice:
        print("❌ Input cannot be empty!")
        return False

    if not choice.lstrip("-").isdigit():
        print("❌ Please enter numbers only!")
        return False

    if choice not in valid_choices:
        print("❌ Invalid choice! Select a number from the menu.")
        return False

    return True

def validate_club_number(club_number, total_clubs):

    club_number = club_number.strip()

    if not club_number:
        print("❌ Club number cannot be empty!")
        return False

    if not club_number.isdigit():
        print("❌ Please enter a valid number!")
        return False

    club_number = int(club_number)

    if club_number < 1 or club_number > total_clubs:
        print(f"❌ Please choose a number between 1 and {total_clubs}!")
        return False

    return True