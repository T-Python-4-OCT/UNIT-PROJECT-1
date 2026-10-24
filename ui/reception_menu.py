from datetime import date, datetime, timedelta

from services import appointment_service as appts
from services import billing_service, clinic_service, patient_service
from ui.common import confirm, need
from ui.shell import run_shell
from utils.formatters import invoice_text, table
from utils.validators import WEEKDAYS, parse_date, parse_day, parse_int, parse_time

RECALL_DAYS = 180


# ---------------------------------------------------------------- patients
def cmd_add_patient(user, args):
    need(args, 0)
    name = input("Full name: ")
    phone = input("Phone: ")
    age = parse_int(input("Age: "), "age")
    blood = input("Blood type (e.g. O+, empty if unknown): ").strip() or "Unknown"
    allergies = [a.strip() for a in input("Allergies (comma separated, empty if none): ").split(",")
                 if a.strip()]
    p = patient_service.add(name, phone, age, blood, allergies)
    print(f"✅ Patient registered: {p.full_name} (ID {p.id}).")


def _patients_table(patients):
    return table(["ID", "Name", "Phone", "Age"],
                 [(p.id, p.full_name, p.phone, p.age) for p in patients])


def cmd_patients(user, args):
    need(args, 0)
    items = patient_service.all_patients()
    print(_patients_table(items) if items else "No patients yet.")


def cmd_search(user, args):
    need(args, 1, 10)
    found = patient_service.search(" ".join(args))
    print(_patients_table(found) if found else "No matching patients.")


def cmd_patient(user, args):
    need(args, 1)
    p = patient_service.get(args[0])
    print(f"👤 {p.full_name} | ID: {p.id} | Phone: {p.phone} | Age: {p.age} | Blood: {p.blood_type}")
    print(f"⚠️  Allergies: {', '.join(p.allergies) or 'None'}")
    if p.notes:
        print(f"📝 Notes: {p.notes}")
    visits = appts.for_patient(p.id)
    if visits:
        print(table(["Appt ID", "Date", "Time", "Clinic", "Status"],
                    [(a.id, a.date, a.time, clinic_service.get(a.clinic_id).name, a.status)
                     for a in visits]))
    else:
        print("No appointments yet.")


def cmd_edit_patient(user, args):
    need(args, 3, 20)
    p = patient_service.get(args[0])
    patient_service.update(p.id, args[1], " ".join(args[2:]))
    print(f"✅ Patient #{p.id} updated ({args[1]}).")


def cmd_delete_patient(user, args):
    need(args, 1)
    p = patient_service.get(args[0])
    if confirm(f"Delete {p.full_name}?"):
        patient_service.delete(p.id)
        print("✅ Patient deleted.")
    else:
        print("Cancelled.")


def cmd_recall(user, args):
    need(args, 0)
    rows = []
    for p in patient_service.all_patients():
        last = appts.last_visit(p.id)
        if last is None:
            rows.append((p.id, p.full_name, p.phone, "never"))
        elif (date.today() - parse_date(last)).days >= RECALL_DAYS:
            rows.append((p.id, p.full_name, p.phone, last))
    print("📞 Patients to call (no visit for 6+ months):")
    print(table(["ID", "Name", "Phone", "Last visit"], rows) if rows else "   Nobody. 🎉")


# ---------------------------------------------------------------- clinics
def cmd_add_clinic(user, args):
    need(args, 0)
    name = input("Clinic name (e.g. Pediatrics): ")
    doctor = input("Doctor name: ")
    fee = float(parse_int(input("Consultation fee (SAR): "), "fee"))
    c = clinic_service.add(name, doctor, fee)
    print(f"✅ Clinic added: {c.name} ({c.doctor}), ID {c.id}. Default hours: Sun-Thu 09:00-14:00.")


def cmd_clinics(user, args):
    need(args, 0)
    print(table(["ID", "Clinic", "Doctor", "Fee"],
                [(c.id, c.name, c.doctor, f"{c.fee:.0f} SAR") for c in clinic_service.all_clinics()]))


def cmd_clinic_fee(user, args):
    need(args, 2)
    c = clinic_service.get(args[0])
    clinic_service.set_fee(c.id, float(parse_int(args[1], "fee")))
    print(f"✅ {c.name} fee set to {args[1]} SAR.")


def cmd_hours(user, args):
    need(args, 1)
    c = clinic_service.get(args[0])
    rows = [(d.title(), " - ".join(c.working_hours[d])) for d in WEEKDAYS if d in c.working_hours]
    print(table(["Day", "Hours"], rows) if rows else f"{c.name} has no working hours.")


def cmd_set_hours(user, args):
    need(args, 3, 4)
    c = clinic_service.get(args[0])
    day = parse_day(args[1])
    if args[2].lower() == "off":
        clinic_service.day_off(c.id, day)
        print(f"✅ {c.name}: {day.title()} is now a day off.")
        return
    need(args, 4)
    start, end = parse_time(args[2]), parse_time(args[3])
    clinic_service.set_hours(c.id, day, start, end)
    print(f"✅ {c.name}: {day.title()} hours set to {start} - {end}.")


def cmd_remove_clinic(user, args):
    need(args, 1)
    c = clinic_service.get(args[0])
    if confirm(f"Remove clinic {c.name}?"):
        clinic_service.remove(c.id)
        print("✅ Clinic removed.")
    else:
        print("Cancelled.")


# ---------------------------------------------------------------- appointments
def cmd_slots(user, args):
    need(args, 1, 2)
    clinic = clinic_service.get(args[0])
    if len(args) == 2:
        dates = [parse_date(args[1]).isoformat()]
    else:
        dates = [(date.today() + timedelta(days=i)).isoformat() for i in range(14)]
    shown = 0
    for d in dates:
        free = appts.free_slots(clinic, d)
        if free:
            print(f"📅 {d} ({parse_date(d).strftime('%A')}): {', '.join(free)}")
            shown += 1
            if len(args) == 1 and shown == 3:
                break
    if not shown:
        print(f"No free slots for {clinic.name}.")


def cmd_next_available(user, args):
    need(args, 1, 2)
    clinic = clinic_service.get(args[0])
    result = appts.next_available(clinic)
    if result is None:
        print(f"No free slots for {clinic.name} in the next 60 days.")
        return
    d, t = result
    print(f"🔎 Nearest free slot in {clinic.name}:")
    print(f"   📅 {parse_date(d).strftime('%A')} {d} at {t}")
    if len(args) == 2:
        patient = patient_service.get(args[1])
        if confirm(f"Book it for {patient.full_name}?"):
            appt = appts.book(patient.id, clinic, d, t)
            print(f"✅ Appointment #{appt.id} confirmed!")


def cmd_book(user, args):
    need(args, 4)
    patient = patient_service.get(args[0])
    clinic = clinic_service.get(args[1])
    appt = appts.book(patient.id, clinic, args[2], args[3])
    print(f"✅ Appointment #{appt.id}: {patient.full_name} at {clinic.name} "
          f"on {appt.date} at {appt.time}.")


def cmd_cancel(user, args):
    need(args, 1)
    appt = appts.cancel(parse_int(args[0], "appointment id"))
    print(f"✅ Appointment #{appt.id} cancelled.")


def cmd_reschedule(user, args):
    need(args, 3)
    appt = appts.get_appointment(parse_int(args[0], "appointment id"))
    clinic = clinic_service.get(appt.clinic_id)
    appts.reschedule(appt, clinic, args[1], args[2])
    print(f"✅ Appointment #{appt.id} moved to {appt.date} at {appt.time}.")


def cmd_appointments(user, args):
    need(args, 0, 1)
    d = parse_date(args[0]).isoformat() if args else date.today().isoformat()
    items = appts.for_date(d)
    print(f"📋 Appointments on {d} ({parse_date(d).strftime('%A')})")
    if not items:
        print("   (none)")
        return
    print(table(["ID", "Time", "Patient", "Clinic", "Status"],
                [(a.id, a.time, patient_service.get(a.patient_id).full_name,
                  clinic_service.get(a.clinic_id).name, a.status) for a in items]))


def cmd_checkin(user, args):
    need(args, 1)
    appt = appts.check_in(parse_int(args[0], "appointment id"))
    print(f"✅ {patient_service.get(appt.patient_id).full_name} checked in at {datetime.now():%H:%M}.")


def cmd_done(user, args):
    need(args, 1)
    appt = appts.complete(parse_int(args[0], "appointment id"))
    print(f"✅ Appointment #{appt.id} marked as completed.")


# ---------------------------------------------------------------- billing
def cmd_invoice(user, args):
    need(args, 1)
    print(invoice_text(billing_service.build_invoice(parse_int(args[0], "appointment id"))))


def cmd_report(user, args):
    need(args, 0, 1)
    d = date.today().isoformat() if not args or args[0] == "today" else parse_date(args[0]).isoformat()
    r = billing_service.daily_report(d)
    print(f"📊 Daily Report — {d}")
    print(f"   Visits: {r['visits']} | Cancelled: {r['cancelled']} | Revenue: {r['revenue']:,.2f} SAR")
    if r["busiest"]:
        print(f"   Busiest clinic: {r['busiest'][0]} ({r['busiest'][1]} visit(s))")


# ---------------------------------------------------------------- command table
COMMANDS = {
    "add_patient": (cmd_add_patient, "add_patient", "Register a new patient"),
    "patients": (cmd_patients, "patients", "List all patients"),
    "search": (cmd_search, "search <name|phone>", "Search patients"),
    "patient": (cmd_patient, "patient <id|phone|name>", "Patient file + visit history"),
    "edit_patient": (cmd_edit_patient, "edit_patient <id> <field> <value>", "Edit name/phone/age/blood/allergies/notes"),
    "delete_patient": (cmd_delete_patient, "delete_patient <id>", "Delete a patient"),
    "recall": (cmd_recall, "recall", "Patients not seen for 6+ months"),
    "add_clinic": (cmd_add_clinic, "add_clinic", "Add a clinic"),
    "clinics": (cmd_clinics, "clinics", "List clinics"),
    "clinic_fee": (cmd_clinic_fee, "clinic_fee <clinic> <fee>", "Change consultation fee"),
    "hours": (cmd_hours, "hours <clinic>", "Show clinic working hours"),
    "set_hours": (cmd_set_hours, "set_hours <clinic> <day> <start> <end> | off", "Set clinic hours"),
    "remove_clinic": (cmd_remove_clinic, "remove_clinic <clinic>", "Remove a clinic"),
    "slots": (cmd_slots, "slots <clinic> [date]", "Free slots"),
    "next_available": (cmd_next_available, "next_available <clinic> [patient]", "Nearest slot (and book it)"),
    "book": (cmd_book, "book <patient> <clinic> <date> <time>", "Book an appointment"),
    "cancel": (cmd_cancel, "cancel <appointment_id>", "Cancel an appointment"),
    "reschedule": (cmd_reschedule, "reschedule <id> <date> <time>", "Move an appointment"),
    "appointments": (cmd_appointments, "appointments [date]", "Appointments of a day (default today)"),
    "checkin": (cmd_checkin, "checkin <appointment_id>", "Check a patient in"),
    "done": (cmd_done, "done <appointment_id>", "Mark visit as completed"),
    "invoice": (cmd_invoice, "invoice <appointment_id>", "Print an invoice"),
    "report": (cmd_report, "report [today|date]", "Daily report"),
}


def run(user):
    return run_shell(user, COMMANDS)