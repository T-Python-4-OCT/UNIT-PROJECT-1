# StudyMate

A terminal-based Python app to help students keep track of their university courses, assignments, projects, exams, and notes during the semester.

## What it does

- **Login system:** Simple login and sign-up screen with hidden password input and SHA-256 password hashing. Default login info is loaded from a `.env` file.
- **Dashboard:** Shows estimated GPA (out of 4.00), course averages, overdue tasks, and upcoming exams.
- **Projects tracker:** Lets you break down each course project into custom steps with specific weights (`%`) and points. Marking a step as done updates the progress bar and total score automatically.
- **Tasks, Exams & Notes:** Add, view, update, and delete tasks, exams, and study notes for each subject.
- **Study Timer:** Built-in countdown timer to track study sessions per subject, automatically logging completed sessions into study notes and `activity.log`.

## Files & Folders

- `main.py` - Entry point of the app and main menu loop.
- `models/classes.py` - Contains the main OOP classes (`User`, `Subject`, `Task`, `Project`, `Exam`, `StudyNote`).
- `services/` - Separate files for each section of the app (`auth_service.py`, `dashboard_service.py`, `subject_service.py`, `task_service.py`, `project_service.py`, `exam_service.py`, `note_service.py`, `pomodoro_service.py`).
- `storage.py` - Handles reading and saving data to `studymate_data.json`.
- `utils.py` - Helper functions for `rich` tables and `questionary` inputs.
- `seed.py` - Generates random sample data using `Faker` to test the app quickly.
- `requirements.txt` - List of libraries used in the project.

## Libraries

- `rich`
- `questionary`
- `Faker`
- `python-dotenv`

## Setup & Run

1. Go to the project folder:
   ```bash
   cd UNIT-PROJECT-1
   ```

2. Install the libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have a `.env` file in the project folder with these values:
   ```env
   DEFAULT_USERNAME=student
   DEFAULT_PASSWORD=1234
   DEFAULT_MAJOR=Software Engineering
   DATA_FILE=studymate_data.json
   ```

4. Run the seed script to generate test data:
   ```bash
   python seed.py
   ```

5. Run the app:
   ```bash
   python main.py
   ```

**Default Login:**
- Username: `student`
- Password: `1234`

---
By Ghali Al-Mazmoumi