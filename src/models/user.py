


class User:
    """كلاس الأب الأساسي للمستخدمين"""
    def __init__(self, user_name: str, email: str, role: str):
        self.user_name = user_name
        self.email = email
        self.__role = role  # تغليف الدور لحمايته

    def get_role(self) -> str:
        return self.__role

    def set_role(self, role: str):
        self.__role = role

    def to_dict(self) -> dict:
        return {
            "user_name": self.user_name,
            "email": self.email,
            "role": self.get_role()
        }


class Dispatcher(User):
    """كلاس المنسق/مرسل الشحنات يورث من User"""
    def __init__(self, user_name: str, email: str):
        super().__init__(user_name=user_name, email=email, role="dispatcher")
        self.assigned_shipments = []

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["assigned_shipments"] = self.assigned_shipments
        return data


class Manager(User):
    """كلاس مدير الأزمات والعمليات يورث من User"""
    def __init__(self, user_name: str, email: str, department: str = "Operations"):
        super().__init__(user_name=user_name, email=email, role="manager")
        self.department = department

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["department"] = self.department
        return data

class FieldSupervisor(User):
    def __init__(self, user_name: str, email: str, assigned_crisis_zone: str):
        super().__init__(user_name=user_name, email=email, role="field_supervisor")
        self.assigned_crisis_zone = assigned_crisis_zone

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["assigned_crisis_zone"] = self.assigned_crisis_zone
        return data

class FleetOfficer(User):
    def __init__(self, user_name: str, email: str, specialty: str = "Drones & Trucks"):
        super().__init__(user_name=user_name, email=email, role="fleet_officer")
        self.specialty = specialty  

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["specialty"] = self.specialty
        return data
        
    


    