
print("=" * 50)
print("DAILY NEWS & WEATHER")
print("=" * 50)

while True:
    print("\n1. Today's Top News")
    print("2. Saudi Arabia News")
    print("3. World News")
    print("4. Sports News")
    print("5. Technology News")
    print("6. Check Weather")
    print("7. Change Language")
    print("8. Exit")

    try:
        choice = int(input("Enter your choice: "))

    except ValueError:
        print("Invalid input! Please enter a number.")
        continue

    if choice == 1:
        print("Today's Top News - Coming soon!")

    elif choice == 2:
        print("Saudi Arabia News - Coming soon!")

    elif choice == 3:
        print("World News - Coming soon!")

    elif choice == 4:
        print("Sports News - Coming soon!")

    elif choice == 5:
        print("Technology News - Coming soon!")

    elif choice == 6:
        print("Weather - Coming soon!")

    elif choice == 7:
        print("Language settings - Coming soon!")

    elif choice == 8:
        print("Thank you for using Daily News & Weather!")
        break

    else:
        print("Invalid choice! Please choose from 1 to 8.")
