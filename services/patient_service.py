from models import Patient
from storage import json_store
from utils.errors import ClinicError
from services import appointment_service

# user-friendly field names -> Patient attribute names
FIELDS = {"name": "full_name", "phone": "phone", "age": "age", "blood": "blood_type",
          "allergies": "allergies", "notes": "notes"}


def all_patients():
    return [Patient(**d) for d in json_store.load("patients")]


def _save(items):
    json_store.save("patients", [p.to_dict() for p in items])


def _validate_phone(phone):
    phone = phone.strip().replace(" ", "")
    if not phone.isdigit() or not 7 <= len(phone) <= 15:
        raise ClinicError("Phone must contain 7-15 digits only.")
    return phone


def add(full_name, phone, age, blood_type="Unknown", allergies=None, notes=""):
    full_name = full_name.strip()
    if len(full_name) < 3:
        raise ClinicError("Full name must be at least 3 characters.")
    phone = _validate_phone(phone)
    if not 0 < age < 120:
        raise ClinicError("Age must be between 1 and 119.")
    items = all_patients()
    if any(p.phone == phone for p in items):
        raise ClinicError(f"A patient with phone {phone} already exists.")
    patient = Patient(max((p.id for p in items), default=0) + 1, full_name, phone, age,
                      blood_type, allergies or [], notes)
    items.append(patient)
    _save(items)
    return patient


def get(ref):
    """Find a patient by ID, phone number, or (unique) part of the name."""
    ref = str(ref).strip()
    for p in all_patients():
        if str(p.id) == ref or p.phone == ref:
            return p
    matches = [p for p in all_patients() if ref.lower() in p.full_name.lower()] if ref else []
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = ", ".join(f"{p.full_name} (ID {p.id})" for p in matches)
        raise ClinicError(f"Several patients match '{ref}': {names}. Use the ID.")
    raise ClinicError(f"No patient found for '{ref}'. Try 'search <text>'.")


def search(text):
    t = text.lower().strip()
    return [p for p in all_patients() if t in p.full_name.lower() or t in p.phone]


def update(patient_id, field_name, value):
    key = field_name.lower()
    if key not in FIELDS:
        raise ClinicError(f"Unknown field '{field_name}'. Use: {', '.join(FIELDS)}.")
    items = all_patients()
    patient = next(p for p in items if p.id == patient_id)
    if key == "phone":
        value = _validate_phone(value)
        if any(p.phone == value and p.id != patient_id for p in items):
            raise ClinicError("Another patient already has this phone number.")
    elif key == "age":
        if not value.strip().isdigit() or not 0 < int(value) < 120:
            raise ClinicError("Age must be a number between 1 and 119.")
        value = int(value)
    elif key == "allergies":
        value = [a.strip() for a in value.split(",") if a.strip()]
    elif key == "name" and len(value.strip()) < 3:
        raise ClinicError("Full name must be at least 3 characters.")
    setattr(patient, FIELDS[key], value)
    _save(items)
    return patient


def delete(patient_id):
    if appointment_service.has_appointments_for_patient(patient_id):
        raise ClinicError("Cannot delete: this patient has appointments on record.")
    items = all_patients()
    _save([p for p in items if p.id != patient_id])
    