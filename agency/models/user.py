from dataclasses import asdict, dataclass, fields


# مستخدم: عميل أو مدير، مع كلمة سر مشفرة (hash) وليس الأصلية.
@dataclass
class User:
    id: int
    username: str
    password_hash: str
    full_name: str
    email: str
    role: str
    phone: str = ""

    # تحوّل المستخدم إلى قاموس عشان ينحفظ في ملف JSON.
    def to_dict(self) -> dict:
        return asdict(self)

    # تبني مستخدم من قاموس مقروء من الملف.
    @staticmethod
    def from_dict(data: dict) -> "User":
        known = {model_field.name for model_field in fields(User)}
        return User(**{key: value for key, value in data.items() if key in known})
