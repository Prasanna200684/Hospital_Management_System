# --- Custom Exceptions ---
class DoctorNotFoundException(Exception): pass
class PatientNotFoundException(Exception): pass
class AppointmentAlreadyExistsException(Exception): pass
class InvalidAgeException(Exception): pass
class InvalidFeeException(Exception): pass
class BillingException(Exception): pass
class Person:
    def __init__(self, id, name, age, phone):
        self.id, self.name, self.age, self.phone = id, name, age, phone

class Doctor(Person):
    def __init__(self, did, name, age, phone, spec, fee):
        super().__init__(did, name, age, phone)
        self.specialization, self.__fee = spec, fee

    def get_consultation_fee(self): return self.__fee

    def set_consultation_fee(self, fee):
        if fee <= 0: raise InvalidFeeException("Fee must be > 0.")
        self.__fee = fee

    def display_details(self):
        print(f"\n--- Doctor ---\n  ID: {self.id} | Name: {self.name} | Age: {self.age}"
              f" | Phone: {self.phone}\n  Specialization: {self.specialization} | Fee: Rs.{self.__fee}")

class Patient(Person):
    def __init__(self, pid, name, age, phone, disease):
        super().__init__(pid, name, age, phone)
        self.disease, self.admission_status = disease, "Admitted"
        self.__history = []

    def get_medical_history(self): return self.__history
    def add_medical_history(self, rec): self.__history.append(rec)

    def display_details(self):
        print(f"\n--- Patient ---\n  ID: {self.id} | Name: {self.name} | Age: {self.age}"
              f" | Phone: {self.phone}\n  Disease: {self.disease} | Status: {self.admission_status}")

class Appointment:
    def __init__(self, aid, did, pid, date, time):
        self.appointment_id, self.doctor_id, self.patient_id = aid, did, pid
        self.date, self.time = date, time

class Bill:
    def __init__(self, bid, pid, consult, meds, lab):
        self.bill_id, self.patient_id = bid, pid
        self.consultation_fee, self.medicine_charges, self.lab_charges = consult, meds, lab
        self.total_amount = consult + meds + lab

    def display_bill(self):
        print(f"\n--- Bill {self.bill_id} | Patient: {self.patient_id} ---"
              f"\n  Consult: Rs.{self.consultation_fee} | Meds: Rs.{self.medicine_charges}"
              f" | Lab: Rs.{self.lab_charges}\n  Total: Rs.{self.total_amount}")
class HospitalManagementSystem:
    def __init__(self):
        self.doctors, self.patients = {}, {}
        self.appointments, self.bills = [], []
        self.diseases, self.bill_counter = set(), 1

    def _validate(self, age, phone, fee=None):
        if age <= 0: raise InvalidAgeException("Age must be > 0.")
        if len(str(phone)) != 10: raise ValueError("Phone must be 10 digits.")
        if fee is not None and fee <= 0: raise InvalidFeeException("Fee must be > 0.")

    def add_doctor(self, did, name, age, phone, spec, fee):
        if did in self.doctors: print(f"  Error: Doctor '{did}' exists."); return
        self._validate(age, phone, fee)
        self.doctors[did] = Doctor(did, name, age, phone, spec, fee)
        print(f"  Doctor '{name}' registered!")

    def search_doctor(self, did):
        if did not in self.doctors: raise DoctorNotFoundException(f"Doctor '{did}' not found.")
        self.doctors[did].display_details()

    def view_all_doctors(self):
        if not self.doctors: print("  No doctors registered."); return
        [d.display_details() for d in self.doctors.values()]

    def update_doctor_fee(self, did, fee):
        if did not in self.doctors: raise DoctorNotFoundException(f"Doctor '{did}' not found.")
        self.doctors[did].set_consultation_fee(fee)
        print(f"  Fee updated to Rs.{fee}.")

    def remove_doctor(self, did):
        if did not in self.doctors: raise DoctorNotFoundException(f"Doctor '{did}' not found.")
        del self.doctors[did]; print(f"  Doctor '{did}' removed.")

    def register_patient(self, pid, name, age, phone, disease):
        if pid in self.patients: print(f"  Error: Patient '{pid}' exists."); return
        self._validate(age, phone)
        self.patients[pid] = Patient(pid, name, age, phone, disease)
        self.diseases.add(disease)
        print(f"  Patient '{name}' registered!")

    def search_patient(self, pid):
        if pid not in self.patients: raise PatientNotFoundException(f"Patient '{pid}' not found.")
        self.patients[pid].display_details()

    def view_all_patients(self):
        if not self.patients: print("  No patients registered."); return
        [p.display_details() for p in self.patients.values()]

    def book_appointment(self, aid, did, pid, date, time):
        if did not in self.doctors: raise DoctorNotFoundException(f"Doctor '{did}' not found.")
        if pid not in self.patients: raise PatientNotFoundException(f"Patient '{pid}' not found.")
        if any(a.doctor_id == did and a.date == date and a.time == time for a in self.appointments):
            raise AppointmentAlreadyExistsException(f"Doctor '{did}' busy on {date} at {time}.")
        self.appointments.append(Appointment(aid, did, pid, date, time))
        print(f"  Appointment '{aid}' booked!")

    def view_appointments(self):
        if not self.appointments: print("  No appointments."); return
        for a in self.appointments:
            d = self.doctors.get(a.doctor_id, type('', (), {'name': 'Unknown'})()).name
            p = self.patients.get(a.patient_id, type('', (), {'name': 'Unknown'})()).name
            print(f"\n  [{a.appointment_id}] Dr.{d} + {p} | {a.date} {a.time}")

    def cancel_appointment(self, aid):
        for a in self.appointments:
            if a.appointment_id == aid:
                self.appointments.remove(a); print(f"  Appointment '{aid}' cancelled."); return
        print(f"  Appointment '{aid}' not found.")

    def add_treatment(self, pid, desc):
        if pid not in self.patients: raise PatientNotFoundException(f"Patient '{pid}' not found.")
        self.patients[pid].add_medical_history(desc)
        print(f"  Treatment added for '{pid}'.")

    def view_treatment_history(self, pid):
        if pid not in self.patients: raise PatientNotFoundException(f"Patient '{pid}' not found.")
        history = self.patients[pid].get_medical_history()
        if not history: print("  No records."); return
        print(f"\n--- Treatment History: {pid} ---")
        for i, r in enumerate(history, 1): print(f"  {i}. {r}")

    def generate_bill(self, pid, consult, meds, lab):
        if pid not in self.patients: raise PatientNotFoundException(f"Patient '{pid}' not found.")
        if any(x < 0 for x in (consult, meds, lab)): raise BillingException("Charges cannot be negative.")
        bill = Bill(f"BILL{self.bill_counter:03d}", pid, consult, meds, lab)
        self.bill_counter += 1
        self.bills.append(bill); bill.display_bill()

    def discharge_patient(self, pid):
        if pid not in self.patients: raise PatientNotFoundException(f"Patient '{pid}' not found.")
        self.patients[pid].admission_status = "Discharged"
        print(f"  Patient '{pid}' discharged.")

    def generate_report(self):
        print(f"\n===== HOSPITAL REPORT =====\n"
              f"  Doctors: {len(self.doctors)} | Patients: {len(self.patients)}\n"
              f"  Appointments: {len(self.appointments)} | Diseases: {self.diseases}\n"
              f"  Revenue: Rs.{sum(b.total_amount for b in self.bills)}\n"
              f"===========================")

def main():
    hms = HospitalManagementSystem()

    hms.add_doctor("D001", "Dr. Ramesh", 45, 9876543210, "Cardiology", 800)
    hms.add_doctor("D002", "Dr. Priya",  38, 9876501234, "Neurology",  1000)
    hms.add_doctor("D003", "Dr. Suresh", 52, 9123456780, "Orthopedics", 600)
    hms.view_all_doctors()

    hms.register_patient("P001", "Anil Kumar",  34, 9000011111, "Diabetes")
    hms.register_patient("P002", "Sunita Devi", 28, 9000022222, "Migraine")
    hms.register_patient("P003", "Ravi Teja",   60, 9000033333, "Arthritis")
    hms.view_all_patients()

    hms.book_appointment("A001", "D001", "P001", "2025-07-10", "10:00 AM")
    hms.book_appointment("A002", "D002", "P002", "2025-07-10", "11:00 AM")
    hms.book_appointment("A003", "D003", "P003", "2025-07-11", "09:00 AM")

    try:
        hms.book_appointment("A004", "D001", "P002", "2025-07-10", "10:00 AM")
    except AppointmentAlreadyExistsException as e:
        print(f"  Caught: {e}")

    hms.view_appointments()

    hms.add_treatment("P001", "Prescribed Metformin 500mg.")
    hms.add_treatment("P001", "Advised low-sugar diet and daily walk.")
    hms.add_treatment("P002", "Prescribed pain reliever.")
    hms.view_treatment_history("P001")

    hms.generate_bill("P001", 800, 300, 150)
    hms.generate_bill("P002", 1000, 200, 0)

    hms.search_doctor("D002")
    hms.search_patient("P003")
    hms.update_doctor_fee("D001", 950)
    hms.discharge_patient("P001")
    hms.search_patient("P001")

    try:
        hms.register_patient("P999", "Test", -5, 9000099999, "Fever")
    except InvalidAgeException as e:
        print(f"  Caught: {e}")

    hms.generate_report()

if __name__ == "__main__":
    main()