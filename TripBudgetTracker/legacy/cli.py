
def run():
    while True:
        print("==============================")
        print("   TRIP BUDGET TRACKER")
        print("==============================")
        print("1. Create a Trip")
        print("2. View Budget")
        print("3. Add Expense")
        print("4. View Expenses")
        print("5. Exit")

        choice = input("Choose an option: ")

        
        if choice == "1":
            traveler_name = input("Enter traveler name: ")
            print("Welcome,", traveler_name)
            print("Trip creation started!")


        elif choice == "2":
            print("View Budget selected")

        elif choice == "3":
            print("Add Expense selected")

        elif choice == "4":
            print("View Expenses selected")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")
