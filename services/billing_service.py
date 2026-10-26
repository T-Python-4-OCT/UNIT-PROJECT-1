from collections import Counter

from services import appointment_service, clinic_service, patient_service
from utils.errors import ClinicError

VAT_RATE = 0.15


def build_invoice(appt_id):
    """Collect everything needed to print an invoice for an appointment."""
    appt = appointment_service.get_appointment(appt_id)
    if appt.status == "cancelled":
        raise ClinicError("Cannot invoice a cancelled appointment.")
    patient = patient_service.get(appt.patient_id)
    clinic = clinic_service.get(appt.clinic_id)

    lines = [("Consultation fee", float(clinic.fee))]
    subtotal = sum(amount for _, amount in lines)
    vat = round(subtotal * VAT_RATE, 2)
    return {"appointment": appt, "patient": patient, "clinic": clinic, "lines": lines,
            "subtotal": subtotal, "vat": vat, "total": round(subtotal + vat, 2)}


def daily_report(date_str):
    """Summary of one day: visits, cancellations, revenue, busiest clinic."""
    appts = appointment_service.for_date(date_str)
    visits = [a for a in appts if a.status != "cancelled"]
    revenue = sum(build_invoice(a.id)["total"] for a in visits
                  if a.status in ("checked_in", "completed"))
    busiest = None
    if visits:
        clinic_id, n = Counter(a.clinic_id for a in visits).most_common(1)[0]
        busiest = (clinic_service.get(clinic_id).name, n)
    return {"visits": len(visits), "cancelled": len(appts) - len(visits),
            "revenue": revenue, "busiest": busiest}