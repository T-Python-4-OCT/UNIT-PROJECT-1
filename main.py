"""VOX Cinema Booking - start the program with:  python main.py"""

from colorama import init

from cinema.ui.display import print_info, print_title


def main() -> None:
    init()  # makes colors work on Windows too
    print_title("🎬  VOX CINEMAS - RIYADH  🎬")
    print_info("Welcome! The booking system is under construction.")


if __name__ == "__main__":
    main()
