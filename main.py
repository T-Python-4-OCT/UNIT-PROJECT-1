from utils import console, print_header, prompt_select, show_spinner


def main():
    show_spinner("Starting StudyMate Academic Assistant...")

    while True:
        print_header(
            "StudyMate — Smart University Academic Assistant",
            "Main Menu: Choose a section below using Up/Down arrow keys and press Enter"
        )

        choices = [
            "1. Academic Progress & Grades Dashboard",
            "2. Manage Subjects",
            "3. Manage Tasks & Assignments",
            "4. Manage Exams",
            "5. Manage Study Notes",
            "6. Save and Exit"
        ]

        choice = prompt_select("Select a section to open:", choices)

        if choice is None or "6." in choice:
            show_spinner("Saving your academic records...")
            console.print("\n[bold cyan]All data saved in StudyMate. Goodbye![/bold cyan]\n")
            break
        elif "1." in choice:
            console.print("[yellow]-> Dashboard section (Coming soon!)[/yellow]")
        elif "2." in choice:
            console.print("[yellow]-> Subjects section (Coming soon!)[/yellow]")
        elif "3." in choice:
            console.print("[yellow]-> Tasks section (Coming soon!)[/yellow]")
        elif "4." in choice:
            console.print("[yellow]-> Exams section (Coming soon!)[/yellow]")
        elif "5." in choice:
            console.print("[yellow]-> Study Notes section (Coming soon!)[/yellow]")


if __name__ == "__main__":
    main()