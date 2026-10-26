# UniMate 🎓

UniMate is a terminal-based Python app I built to help university students manage their semester in one place. It lets you keep track of your courses, tasks, project steps, exams, study notes, and study time directly from the command line.

## Features

- **Login & Registration:** Simple account system with hidden password input and SHA-256 password hashing.
- **Academic Dashboard:** Shows a quick summary of your credit hours, completed tasks, project progress, and average grades, plus a table showing your grade standing (`A` to `F`) for each course.
- **Manage Subjects:** Add, view, and delete courses. The app prevents deleting a course if it still has tasks, projects, or exams linked to it.
- **Tasks & Assignments:** Add tasks with due dates and priority levels (`High`, `Medium`, `Low`), mark them as done, and save your scores.
- **Project Milestones:** Break down any course project into custom steps with percentage weights (`%`). Completing a step automatically updates the progress bar and total score.
- **Exams & Study Notes:** Schedule upcoming exams, record exam scores, and save or read study notes for your courses.
- **Study Timer:** Built-in countdown timer (10-second demo, 25-minute standard, or custom time). When the timer finishes, it logs the session to `activity.log` and saves a note automatically.

## Project Files

- `main.py` - Starts the app and runs the main menu.
- `models/classes.py` - Contains the main OOP classes (`ScoredItem`, `Subject`, `Task`, `Project`, `Exam`, `StudyNote`, `User`).
- `services/` - Menu and logic files for each part of the app:
  - `base_service.py` - Shared menu loop and helper methods inherited by other services.
  - `auth_service.py` - Login and create account screens.
  - `dashboard_service.py` - Overall stats and course performance table.
  - `subject_service.py` - Add, view, and delete courses.
  - `task_service.py` - Manage assignments and task scores.
  - `project_service.py` - Manage projects and milestone steps.
  - `exam_service.py` - Schedule exams and record grades.
  - `note_service.py` - Create, read, and delete study notes.
  - `pomodoro_service.py` - Study countdown timer and activity logger.
- `storage.py` - Loads and saves data to `unimate_data.json`.
- `utils.py` - Input validation functions, `questionary` menus, and `rich` print helpers.
- `seed.py` - Creates fake test data using `Faker` so you can test the app right away.
- `requirements.txt` - List of packages used in the project.

## Libraries Used

- `rich` - For tables, panels, colors, and progress bars.
- `questionary` - For interactive menus and user prompts.
- `Faker` - For generating sample data in `seed.py`.
- `python-dotenv` - For reading default settings from the `.env` file.

## How to Run

1. Clone the repository and go to the project folder:
   ```bash
   cd UNIT-PROJECT-1
   ```

2. Create and activate a virtual environment (optional):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project folder with these default values:
   ```env
   DEFAULT_USERNAME=student
   DEFAULT_PASSWORD=1234
   DEFAULT_MAJOR=Software Engineering
   DATA_FILE=unimate_data.json
   ```

5. Generate sample data to test the app:
   ```bash
   python seed.py
   ```

6. Run the app:
   ```bash
   python main.py
   ```

### Default Login (after running `seed.py`)
- **Username:** `student`
- **Password:** `1234`

---
By **Ghali Al-Mazmoumi**