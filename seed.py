from datetime import date, timedelta
from faker import Faker
from models.classes import Subject, Task, Exam, StudyNote
from storage import save_data

fake = Faker()

def generate_seed():
    try:
        subjects = []
        
        for i in range(1, 5):
            sub_id = f"SUB-{i:03d}"
            code = fake.bothify(text="???###").upper()
            name = fake.catch_phrase().title()
            instructor = f"Dr. {fake.name()}"
            credit_hours = fake.random_int(min=2, max=4)
            
            subjects.append(Subject(sub_id, name, code, instructor, credit_hours))

        tasks = []
        task_counter = 1

        for sub in subjects:
            for _ in range(2):
                t_id = f"TSK-{task_counter:03d}"
                task_counter += 1
                
                title = f"{sub.code} - {fake.bs().title()}"
                description = fake.sentence()
                
                days_offset = fake.random_int(min=-7, max=10)
                due_date = (date.today() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
                priority = fake.random_element(elements=("High", "Medium", "Low"))
                
                if days_offset < 0:
                    status = "Completed"
                    earned = float(fake.random_int(min=75, max=100))
                    max_s = 100.0
                else:
                    status = "Not Started"
                    earned = None
                    max_s = None

                tasks.append(Task(t_id, title, description, sub.subject_id, due_date, priority, status, earned, max_s))

        exams = []
        exam_counter = 1
        
        for sub in subjects:
            e_id = f"EXM-{exam_counter:03d}"
            exam_counter += 1
            
            e_type = fake.random_element(elements=("Midterm", "Final", "Quiz", "Practical"))
            title = f"{sub.code} - {fake.catch_phrase().title()}"
            days_offset = fake.random_int(min=-10, max=15)
            exam_date = (date.today() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            exam_time = fake.time(pattern="%H:%M")
            earned = float(fake.random_int(min=70, max=98)) if days_offset < 0 else None
            
            exams.append(Exam(e_id, title, sub.subject_id, exam_date, exam_time, e_type, earned, 100.0))

        notes = []
        note_counter = 1
        for sub in subjects:
            n_id = f"NTE-{note_counter:03d}"
            note_counter += 1
            title = f"{sub.code} - {fake.bs().title()}"
            content = fake.paragraph(nb_sentences=3)
            notes.append(StudyNote(n_id, title, content, sub.subject_id))

        data = {
            "subjects": subjects,
            "tasks": tasks,
            "exams": exams,
            "notes": notes
        }

        save_data(data)
        print("Seed data generated using Faker.")

    except Exception as e:
        print(f"Error generating seed data: {e}")

if __name__ == "__main__":
    generate_seed()