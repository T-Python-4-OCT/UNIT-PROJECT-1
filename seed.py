from datetime import date, timedelta
from faker import Faker
from models.classes import Subject, Task, Project, Exam, StudyNote
from storage import save_data

fake = Faker()

def generate_seed():
    try:
        # Generate 5 random subjects to showcase different grade scenarios
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

        # Generate term projects using milestone steps
        projects = []
        project_counter = 1
        
        for idx, sub in enumerate(subjects):
            min_s, max_s_range = score_brackets[idx % len(score_brackets)]
            p_id = f"PRJ-{project_counter:03d}"
            project_counter += 1
            title = f"{sub.code} Project: {fake.catch_phrase().title()}"
            deadline = (date.today() + timedelta(days=fake.random_int(min=5, max=40))).strftime("%Y-%m-%d")
            
            steps_done_count = fake.random_int(min=1, max=5)
            completed_steps = Project.MILESTONES[:steps_done_count]
            earned = float(fake.random_int(min=min_s, max=max_s_range)) if steps_done_count == 5 else None
                
            projects.append(Project(p_id, title, sub.subject_id, deadline, completed_steps=completed_steps, earned_score=earned, max_score=100.0))

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
            "subjects": subjects,
            "tasks": tasks,
            "projects": projects,
            "exams": exams,
            "notes": notes
        }

        save_data(data)
        print("Seed data generated successfully with milestone-based projects!")

    except Exception as e:
        print(f"Error generating seed data: {e}")

if __name__ == "__main__":
    generate_seed()