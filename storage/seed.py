from datetime import date, timedelta

from models import Appointment, Clinic, Patient, Receptionist, hash_password
from storage import json_store

WORK_DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday"]


def default_hours():
    return {day: ["09:00", "14:00"] for day in WORK_DAYS}


def seed_if_empty():
    """Create demo data the first time the program runs."""
    if json_store.load("receptionists"):
        return

    json_store.save("receptionists",
                    [Receptionist(1, "reception", hash_password("1234"), "Reem Hassan").to_dict()])

    clinics = [
        Clinic(1, "Cardiology", "Dr. Ahmed Ali", 200, default_hours()),
        Clinic(2, "Dermatology", "Dr. Noura Saad", 150, default_hours()),
        Clinic(3, "General", "Dr. Khalid Omar", 100, default_hours()),
    ]
    json_store.save("clinics", [c.to_dict() for c in clinics])

    patients = [
        Patient(1, "Sara Mohammed", "0501234567", 29, "O+", ["penicillin"]),
        Patient(2, "Faisal Nasser", "0559876543", 41, "A+", []),
    ]
    json_store.save("patients", [p.to_dict() for p in patients])

    # One old completed visit so the 'recall' feature has data later.
    past = (date.today() - timedelta(days=220)).isoformat()
    json_store.save("appointments",
                    [Appointment(1, 1, 3, past, "10:00", status="completed").to_dict()])