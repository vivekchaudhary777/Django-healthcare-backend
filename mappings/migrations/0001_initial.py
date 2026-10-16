import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial"), ("doctors", "0001_initial"), ("patients", "0001_initial")]
    operations = [migrations.CreateModel(name="PatientDoctorMapping", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="doctor_mappings", to=settings.AUTH_USER_MODEL)),
        ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="patient_mappings", to="doctors.doctor")),
        ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="doctor_mappings", to="patients.patient")),
    ], options={"ordering": ["id"], "constraints": [models.UniqueConstraint(fields=("patient", "doctor"), name="unique_patient_doctor_mapping")]})]
