import questionary
from auth.users import login_page, create_account_page

def main():
    while True:
        print("\n" + "="*50)
        print("    Learn with Excellence, Grow with Skills")
        print("="*50)
        
        choice = questionary.select(
            "Choose an option:",
            choices=[
                "Log In",
                
                "Create Trainee Account",
                "Browse Training Courses",
                "Search for a Course",
                "View Trainers",
                "Verify Certificate",
                "About the Academy",
                "Exit"
            ]
        ).ask()

        if choice == "Log In":
            login_page()
            
        elif choice == "Create Trainee Account":
            create_account_page()
            
        elif choice == "Browse Training Courses":
            print("\n[+] Loading Available Courses...")
            
        elif choice == "Search for a Course":
            print("\n[+] Course Search Engine...")
            
        elif choice == "View Trainers":
            print("\n[+] Loading Trainers List...")
            
        elif choice == "Verify Certificate":
            print("\n[+] Certificate Verification Portal...")
            
        elif choice == "About the Academy":
            print("\n[About Us]")
            print("Learn with Excellence, Grow with Skills Academy is dedicated to providing top-notch professional training.")
            
        elif choice == "Exit" or choice is None:
            print("\nThank you for using our system. Goodbye!")
            break

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()