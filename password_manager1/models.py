class VaultItem:
    def __init__(self, site_name, username, password):
        self.site_name = site_name
        self.username = username
        self.password = password

    def to_dict(self):
        return {
            "site_name": self.site_name,
            "username": self.username,
            "password": self.password
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["site_name"], data["username"], data["password"])

    def get_masked_password(self):
        
        if len(self.password) <= 3:
            return "***"
        return "*" * (len(self.password) - 3) + self.password[-3:]

    def __str__(self):
        masked_pwd = self.get_masked_password()
        return f"Site: {self.site_name} | Username: {self.username} | Password: {masked_pwd}"