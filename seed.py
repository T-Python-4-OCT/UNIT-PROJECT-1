from datetime import date, timedelta
from faker import Faker
from models.classes import Subject, Task, Exam, StudyNote
from storage import save_data

fake = Faker()

def generate_seed():
    try:
        subjects_data = [
            ("Software Engineering", "SWE301", "Dr. Ahmed", 3),
            ("Human-Computer Interaction", "HCI202", "Dr. Sarah", 3),
            ("Database Systems", "CIS311", "Dr. Mohammed", 4),
            ("Web Development", "SWE363", "Dr. Faisal", 3),
        ]

        subjects = []
        for i, (name, code, instructor, hours) in enumerate(subjects_data, start=1):
            sub_id = f"SUB-{i:03d}"
            subjects.append(Subject(sub_id, name, code, instructor, hours))

        tasks = []
        task_counter = 1
        priorities = ["High", "Medium", "Low"]

        for sub in subjects:
            for j in range(1, 3):
                t_id = f"TSK-{task_counter:03d}"
                task_counter += 1
                
                title = f"{sub.code} - Assignment {j}"
                description = fake.sentence()
                
                days_offset = fake.random_int(min=-7, max=10)
                due_date = (date.today() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
                priority = fake.random_element(elements=priorities)
                
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
            
            title = f"{sub.code} Midterm"
            days_offset = fake.random_int(min=-10, max=15)
            exam_date = (date.today() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            earned = float(fake.random_int(min=70, max=98)) if days_offset < 0 else None
            
            exams.append(Exam(e_id, title, sub.subject_id, exam_date, "10:00", "Midterm", earned, 100.0))

        notes = []
        note_counter = 1
        for sub in subjects:
            n_id = f"NTE-{note_counter:03d}"
            note_counter += 1
            title = f"{sub.name} Summary"
            content = fake.text(max_nb_chars=120)
            notes.append(StudyNote(n_id, title, content, sub.subject_id))

        data = {
            "subjects": [s.to_dict() for s in subjects],
            "tasks": [t.to_dict() for t in tasks],
            "exams": [e.to_dict() for e in exams],
            "notes": [n.to_dict() for n in notes]
        }

        save_data(data)
        print("Seed data generated successfully.")

    except Exception as e:
        print(f"Error generating seed data: {e}")

if __name__ == "__main__":
    generate_seed()