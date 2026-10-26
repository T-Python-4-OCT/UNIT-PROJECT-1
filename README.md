# Training Courses Learning Platform


### Overview

MOTQEN Academy is a Python-based command-line application for managing training courses and academy activities. It uses JSON files to store data and provides different features based on user roles.

**Slogan:** Learn with Excellence, Grow with Skills.

### User Roles & Features

* **Admin:** Manages academy activities and users.
* **Trainer:** Views assigned courses and trainees, records attendance, and manages grades.
* **Trainee:** Browses and enrolls in courses, tracks lesson progress, and views attendance and grades.

### Main Features

* User registration and login.
* Browse and search training courses.
* View trainers and enroll in courses.
* Manage attendance and grades.
* Track course progress.
* Interactive menu with arrow-key navigation.

### Technologies

* Python
* JSON for data storage
* `prompt_toolkit` for interactive menus
* Git and GitHub for version control

### Usage

1. Install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   python main.py
   ```

3. Use the arrow keys to navigate the menu and press **Enter** to select an option.

### Project Structure

The code is organized into modules and packages, including:

* `auth/` — User accounts and role-specific pages.
* `courses/` — Course browsing and searching.
* `training/` — Training activities and progress.
* `utils/` — Shared utilities.
* `data/` — JSON data files.
* `main.py` — Application entry point.
* `requirements.txt` — Required Python packages.

### Installation Requirements

Generate the package list before submission:

```bash
python -m pip freeze > requirements.txt
```

### Version Control

Git and GitHub are used to track changes and manage the project.
