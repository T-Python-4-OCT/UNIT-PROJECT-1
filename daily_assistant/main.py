from news import show_top_news,show_saudi_news


print("=" * 50)
print("DAILY NEWS & WEATHER")
print("=" * 50)

while True:
    print("\n1. Today's Top News")
    print("2. Saudi Arabia News")
    print("3. Sports News")
    print("4. Technology News")
    print("5. Check Weather")
    print("6. Exit")

    try:
        choice = int(input("Enter your choice: "))

    except ValueError:
        print("Invalid input! Please enter a number.")
        continue

    if choice == 1:
       show_top_news()
       
    elif choice == 2:
        show_saudi_news()

    elif choice == 3:
        print("Sports News - Coming soon!")
        
        
    elif choice == 4:
        print("Technology News - Coming soon!")
        
    elif choice == 5:
        print("Weather - Coming soon!")

    elif choice == 6:
        print("Thank you for using Daily News & Weather!")
        break

    else:
        print("Invalid choice! Please choose from 1 to 8.")
