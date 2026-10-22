def choose_language():
    print("🌍 TRAVEL EXPLORER")
    print()
    print("1. Arabic 🇸🇦")
    print("2. English 🇺🇸")

    while True:
        choice = input("\n👉 Choose your language: ")

        if choice == "1":
            return "ar"

        if choice == "2":
            return "en"

        print("❌ Invalid choice. Please choose 1 or 2")
