from models.user import User


class Trainer(User):
    def __init__(self, user_id, full_name, email):
        super().__init__(user_id, full_name, email, "trainer")

    def view_trainees(self):
        print(f"{self.full_name} can view enrolled trainees.")
