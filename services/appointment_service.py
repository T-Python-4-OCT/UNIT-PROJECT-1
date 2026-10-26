from datetime import datetime, timedelta

from models import Appointment
from storage import json_store
from utils.errors import ClinicError
from utils.validators import WEEKDAYS, parse_date, parse_time

SLOT_MINUTES = 30
ACTIVE = ("booked", "checked_in")


# ---------------------------------------------------------------- storage helpers
def _load():
    return [Appointment(**d) for d in json_store.load("appointments")]


def _save(items):
    json_store.save("appointments", [a.to_dict() for a in items])


def _update(appt):
    items = _load()
    for i, a in enumerate(items):
        if a.id == appt.id:
            items[i] = appt
    _save(items)


def get_appointment(appt_id):
    for a in _load():
        if a.id == appt_id:
            return a
    raise ClinicError(f"Appointment #{appt_id} not found.")


# ---------------------------------------------------------------- slots
def generate_slots(clinic, date_str):
    """All 30-minute slots in the clinic's working hours for that date."""
    d = parse_date(date_str)
    hours = clinic.working_hours.get(WEEKDAYS[d.weekday()])
    if not hours:
        return []
    cur = datetime.strptime(hours[0], "%H:%M")
    end = datetime.strptime(hours[1], "%H:%M")
    slots = []
    while cur + timedelta(minutes=SLOT_MINUTES) <= end:
        slots.append(cur.strftime("%H:%M"))
        cur += timedelta(minutes=SLOT_MINUTES)
    return slots


def free_slots(clinic, date_str, now=None):
    now = now or datetime.now()
    d = parse_date(date_str)
    if d < now.date():
        return []
    iso = d.isoformat()
    taken = {a.time for a in _load()
             if a.clinic_id == clinic.id and a.date == iso and a.status != "cancelled"}
    result = []
    for s in generate_slots(clinic, iso):
        if s in taken:
            continue
        if d == now.date() and s <= now.strftime("%H:%M"):
            continue
        result.append(s)
    return result


def _ensure_slot_free(clinic, date_str, time_str, now=None):
    free = free_slots(clinic, date_str, now)
    if time_str in free:
        return
    if free:
        raise ClinicError(f"This slot is not available. Try: {', '.join(free[:3])}")
    raise ClinicError(f"{clinic.name} has no free slots on {date_str}.")


def _patient_busy(items, patient_id, d, t, ignore_id=None):
    return any(a.patient_id == patient_id and a.date == d and a.time == t
               and a.status in ACTIVE and a.id != ignore_id for a in items)


# ---------------------------------------------------------------- booking
def book(patient_id, clinic, date_str, time_str, now=None):
    d = parse_date(date_str).isoformat()
    t = parse_time(time_str)
    _ensure_slot_free(clinic, d, t, now)
    items = _load()
    if _patient_busy(items, patient_id, d, t):
        raise ClinicError("The patient already has an appointment at this time.")
    appt = Appointment(max((a.id for a in items), default=0) + 1, patient_id, clinic.id, d, t)
    items.append(appt)
    _save(items)
    return appt


def cancel(appt_id):
    appt = get_appointment(appt_id)
    if appt.status not in ACTIVE:
        raise ClinicError(f"Appointment #{appt_id} is already {appt.status}.")
    appt.status = "cancelled"
    _update(appt)
    return appt


def reschedule(appt, clinic, date_str, time_str, now=None):
    if appt.status != "booked":
        raise ClinicError(f"Only 'booked' appointments can be moved (this one is {appt.status}).")
    d = parse_date(date_str).isoformat()
    t = parse_time(time_str)
    _ensure_slot_free(clinic, d, t, now)
    if _patient_busy(_load(), appt.patient_id, d, t, ignore_id=appt.id):
        raise ClinicError("The patient already has an appointment at this time.")
    appt.date, appt.time = d, t
    _update(appt)
    return appt


def next_available(clinic, now=None, days=60):
    """Return (date, time) of the nearest free slot, or None."""
    now = now or datetime.now()
    for offset in range(days + 1):
        d = (now.date() + timedelta(days=offset)).isoformat()
        free = free_slots(clinic, d, now)
        if free:
            return d, free[0]
    return None


# ---------------------------------------------------------------- queries
def for_patient(patient_id):
    return sorted((a for a in _load() if a.patient_id == patient_id),
                  key=lambda a: (a.date, a.time))


def for_date(date_str):
    d = parse_date(date_str).isoformat()
    return sorted((a for a in _load() if a.date == d), key=lambda a: a.time)


def last_visit(patient_id):
    done = [a.date for a in _load() if a.patient_id == patient_id and a.status == "completed"]
    return max(done) if done else None


def has_appointments_for_patient(patient_id):
    return any(a.patient_id == patient_id for a in _load())


def has_appointments_for_clinic(clinic_id):
    return any(a.clinic_id == clinic_id for a in _load())


# ---------------------------------------------------------------- visit flow
def check_in(appt_id):
    appt = get_appointment(appt_id)
    if appt.status != "booked":
        raise ClinicError(f"Cannot check in: appointment is {appt.status}.")
    appt.status = "checked_in"
    _update(appt)
    return appt


def complete(appt_id):
    appt = get_appointment(appt_id)
    if appt.status not in ACTIVE:
        raise ClinicError(f"Appointment is already {appt.status}.")
    appt.status = "completed"
    _update(appt)
    return appt