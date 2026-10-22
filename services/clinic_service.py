from models import Clinic
from storage import json_store
from storage.seed import default_hours
from utils.errors import ClinicError


def all_clinics():
    return [Clinic(**d) for d in json_store.load("clinics")]


def _save(items):
    json_store.save("clinics", [c.to_dict() for c in items])


def _find(items, clinic_id):
    return next(c for c in items if c.id == clinic_id)


def get(ref):
    """Find a clinic by ID or name (case-insensitive)."""
    ref = str(ref).strip().lower()
    for c in all_clinics():
        if str(c.id) == ref or c.name.lower() == ref:
            return c
    raise ClinicError(f"No clinic found for '{ref}'. Try 'clinics'.")


def add(name, doctor, fee):
    name, doctor = name.strip(), doctor.strip()
    if not name or not doctor:
        raise ClinicError("Clinic name and doctor name are required.")
    if fee <= 0:
        raise ClinicError("Fee must be greater than 0.")
    items = all_clinics()
    if any(c.name.lower() == name.lower() for c in items):
        raise ClinicError(f"Clinic '{name}' already exists.")
    clinic = Clinic(max((c.id for c in items), default=0) + 1, name, doctor, fee, default_hours())
    items.append(clinic)
    _save(items)
    return clinic


def set_fee(clinic_id, fee):
    if fee <= 0:
        raise ClinicError("Fee must be greater than 0.")
    items = all_clinics()
    clinic = _find(items, clinic_id)
    clinic.fee = fee
    _save(items)
    return clinic


def set_hours(clinic_id, day, start, end):
    if start >= end:
        raise ClinicError("Start time must be before end time.")
    items = all_clinics()
    clinic = _find(items, clinic_id)
    clinic.working_hours[day] = [start, end]
    _save(items)
    return clinic


def day_off(clinic_id, day):
    items = all_clinics()
    clinic = _find(items, clinic_id)
    clinic.working_hours.pop(day, None)
    _save(items)
    return clinic


def remove(clinic_id):
    # NOTE: in step 7 we will block removing clinics that have appointments.
    items = all_clinics()
    _save([c for c in items if c.id != clinic_id])