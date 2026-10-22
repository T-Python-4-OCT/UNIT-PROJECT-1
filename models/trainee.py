from models.user import User


class Trainee(User):
    def __init__(self, user_id, full_name, email):
        super().__init__(user_id, full_name, email, "trainee")

    def view_courses(self):
        print(f"{self.full_name} can view training courses.")
