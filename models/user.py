class User:
    def __init__(self, user_id, full_name, email, role):
        self.id = user_id
        self.full_name = full_name
        self.email = email
        self.role = role
        
    def display_info(self):
        print(f"ID: {self.id}")
        print(f"Name: {self.full_name}")
        print(f"Email: {self.email}")
        print(f"Role: {self.role}")

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)
