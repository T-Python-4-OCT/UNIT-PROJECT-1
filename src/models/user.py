


class User:
    def __init__(self, user_name, email, role):
        self._user_name = user_name
        self._email = email
        self._role = role  

    @property
    def user_name(self):
        return self._user_name

    @property
    def email(self):
        return self._email

    @property
    def role(self):
        return self._role

    def to_dict(self):
        return {
            "user_name": self._user_name,
            "email": self._email,
            "role": self._role
        }


class Dispatcher(User):
    def __init__(self, user_name, email):
        super().__init__(user_name, email, role="dispatcher")


class Manager(User):
    def __init__(self, user_name, email, department="Operations"):
        super().__init__(user_name, email, role="manager")
        self.department = department

    def to_dict(self):
        data = super().to_dict()
        data["department"] = self.department
        return data


class FieldSupervisor(User):
    def __init__(self, user_name, email, crisis_zone):
        super().__init__(user_name, email, role="field_supervisor")
        self.crisis_zone = crisis_zone

    def to_dict(self):
        data = super().to_dict()
        data["crisis_zone"] = self.crisis_zone
        return data


class FleetOfficer(User):
    def __init__(self, user_name, email, specialty="Drones"):
        super().__init__(user_name, email, role="fleet_officer")
        self.specialty = specialty

    def to_dict(self):
        data = super().to_dict()
        data["specialty"] = self.specialty
        return data
        
    


    