from django.conf import settings
from django.db import models


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="doctor_mappings")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT, related_name="patient_mappings")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_mappings")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [models.UniqueConstraint(fields=("patient", "doctor"), name="unique_patient_doctor_mapping")]

    def __str__(self):
        return f"Patient {self.patient_id} - Doctor {self.doctor_id}"
