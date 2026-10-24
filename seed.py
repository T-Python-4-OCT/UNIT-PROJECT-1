import os
from datetime import date, timedelta
from dotenv import load_dotenv
from faker import Faker
from models.classes import User, Subject, Task, Project, Exam, StudyNote
from storage import save_data

# Load environment variables from .env file
load_dotenv()
fake = Faker()

def generate_seed():
    try:
        # Read default student credentials from Environment Variables (.env)
        env_user = os.getenv("DEFAULT_USERNAME", "student")
        env_pass = os.getenv("DEFAULT_PASSWORD", "1234")
        env_major = os.getenv("DEFAULT_MAJOR", "Software Engineering")

        users = [
            User(env_user, fake.name(), env_major, env_pass)
        ]

        # Generate 5 random subjects
        subjects = []
        for i in range(1, 6):
            sub_id = f"SUB-{i:03d}"
            code = fake.bothify(text="???###").upper()
            name = fake.catch_phrase().title()
            instructor = f"Dr. {fake.name()}"
            credit_hours = fake.random_int(min=2, max=4)
            subjects.append(Subject(sub_id, name, code, instructor, credit_hours))

        score_brackets = [
            (92, 100),  # Excellent (A)
            (81, 89),   # Very Good (B)
            (71, 79),   # Good Standing (C)
            (61, 68),   # Needs Attention (D)
            (45, 58)    # At Risk (F)
        ]

        # Generate tasks for each subject
        tasks = []
        task_counter = 1
        for idx, sub in enumerate(subjects):
            min_s, max_s_range = score_brackets[idx % len(score_brackets)]
            for j in range(2):
                t_id = f"TSK-{task_counter:03d}"
                task_counter += 1
                title = f"{sub.code} - {fake.bs().title()}"
                description = fake.sentence()
                
                if j == 0 or fake.boolean(chance_of_getting_true=60):
                    days_offset = fake.random_int(min=-7, max=-1)
                    status = "Completed"
                    earned = float(fake.random_int(min=min_s, max=max_s_range))
                    max_s = 100.0
                else:
                    days_offset = fake.random_int(min=1, max=10)
                    status = "Not Started"
                    earned = None
                    max_s = None

                due_date = (date.today() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
                priority = fake.random_element(elements=("High", "Medium", "Low"))
                tasks.append(Task(t_id, title, description, sub.subject_id, due_date, priority, status, earned, max_s))

        # Generate projects with 5 unique custom steps per subject
        projects = []
        project_counter = 1
        weight_distributions = [
            [15, 20, 25, 25, 15],
            [10, 20, 30, 25, 15],
            [20, 20, 20, 20, 20],
            [15, 15, 30, 20, 20],
            [10, 25, 25, 20, 20]
        ]
        completed_counts = [4, 3, 2, 1, 5]

        for idx, sub in enumerate(subjects):
            min_s, max_s_range = score_brackets[idx % len(score_brackets)]
            p_id = f"PRJ-{project_counter:03d}"
            project_counter += 1
            title = f"{sub.code}: {fake.catch_phrase().title()}"
            deadline = (date.today() + timedelta(days=fake.random_int(min=7, max=40))).strftime("%Y-%m-%d")
            
            weights = weight_distributions[idx % len(weight_distributions)]
            done_steps_target = completed_counts[idx % len(completed_counts)]
            
            custom_steps = []
            for step_num in range(5):
                w = weights[step_num]
                max_pts = float(w)
                is_done = step_num < done_steps_target
                step_name = f"{sub.code} - {fake.bs().title()}"
                
                if is_done:
                    ratio = fake.random_int(min=min_s, max=max_s_range) / 100.0
                    earned_pts = round(max_pts * ratio, 1)
                else:
                    earned_pts = None

                custom_steps.append({
                    "name": step_name,
                    "weight": w,
                    "max_points": max_pts,
                    "earned_points": earned_pts,
                    "completed": is_done
                })

            projects.append(Project(p_id, title, sub.subject_id, deadline, steps=custom_steps))

        # Generate exams
        exams = []
        exam_counter = 1
        for idx, sub in enumerate(subjects):
            min_s, max_s_range = score_brackets[idx % len(score_brackets)]
            e_id = f"EXM-{exam_counter:03d}"
            exam_counter += 1
            e_type = fake.random_element(elements=("Midterm", "Final", "Quiz", "Practical"))
            title = f"{sub.code} - {fake.catch_phrase().title()}"
            days_offset = fake.random_int(min=-10, max=5)
            exam_date = (date.today() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            exam_time = fake.time(pattern="%H:%M")
            
            earned = float(fake.random_int(min=min_s, max=max_s_range))
            exams.append(Exam(e_id, title, sub.subject_id, exam_date, exam_time, e_type, earned, 100.0))

        # Generate study notes
        notes = []
        note_counter = 1
        for sub in subjects:
            n_id = f"NTE-{note_counter:03d}"
            note_counter += 1
            title = f"{sub.code} - {fake.bs().title()}"
            content = fake.paragraph(nb_sentences=3)
            notes.append(StudyNote(n_id, title, content, sub.subject_id))

        # Save all generated data to JSON
        data = {
            "users": users,
            "subjects": subjects,
            "tasks": tasks,
            "projects": projects,
            "exams": exams,
            "notes": notes
        }

        save_data(data)
        print("Seed data generated successfully using Faker and .env variables!")

    except Exception as e:
        print(f"Error generating seed data: {e}")

if __name__ == "__main__":
    generate_seed()