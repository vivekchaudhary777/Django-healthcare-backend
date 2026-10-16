from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient

User = get_user_model()


class HealthcareAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", name="Owner", password="Strong-password-912")
        self.other = User.objects.create_user(email="other@example.com", name="Other", password="Strong-password-912")

    def test_registration_duplicate_case_insensitive_and_login(self):
        response = self.client.post("/api/auth/register/", {
            "name": "New User", "email": "New.User@example.com", "password": "Strong-password-912"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertTrue(User.objects.get(email="new.user@example.com").check_password("Strong-password-912"))
        duplicate = self.client.post("/api/auth/register/", {
            "name": "Duplicate", "email": "NEW.USER@example.com", "password": "Strong-password-912"
        }, format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        login = self.client.post("/api/auth/login/", {
            "email": "OWNER@example.com", "password": "Strong-password-912"
        }, format="json")
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)
        failed = self.client.post("/api/auth/login/", {
            "email": "owner@example.com", "password": "wrong"
        }, format="json")
        self.assertEqual(failed.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(str(failed.data["detail"]), "Invalid email or password.")

    def test_refresh_rotates_and_revokes_old_token(self):
        self.client.force_authenticate(None)
        login = self.client.post("/api/auth/login/", {
            "email": "owner@example.com", "password": "Strong-password-912"
        }, format="json")
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        old_refresh = login.data["refresh"]
        rotated = self.client.post("/api/auth/token/refresh/", {"refresh": old_refresh}, format="json")
        self.assertEqual(rotated.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", rotated.data)
        revoked = self.client.post("/api/auth/token/refresh/", {"refresh": old_refresh}, format="json")
        self.assertEqual(revoked.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_crud_and_owner_isolation(self):
        response = self.client.post("/api/patients/", {"name": "Patient One"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)
        created = self.client.post("/api/patients/", {"name": "Patient One", "gender": "female"}, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        patient_id = created.data["id"]
        self.assertEqual(self.client.get("/api/patients/").data["count"], 1)
        self.assertEqual(self.client.put(f"/api/patients/{patient_id}/", {"name": "Updated"}, format="json").status_code, 200)
        self.assertEqual(self.client.get("/api/patients/999999/").status_code, 404)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/patients/{patient_id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/patients/{patient_id}/").status_code, 404)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f"/api/patients/{patient_id}/").status_code, 204)
        invalid = self.client.post("/api/patients/", {"name": "Bad Date", "date_of_birth": (timezone.localdate() + timedelta(days=1)).isoformat()}, format="json")
        self.assertEqual(invalid.status_code, 400)

    def test_doctor_crud_visibility_and_creator_permissions(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/doctors/", {
            "name": "Ada Doctor", "specialization": "Cardiology", "phone": "555-0101"
        }, format="json")
        self.assertEqual(response.status_code, 201)
        doctor_id = response.data["id"]
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get("/api/doctors/").data["count"], 1)
        self.assertEqual(self.client.get(f"/api/doctors/{doctor_id}/").status_code, 200)
        self.assertEqual(self.client.put(f"/api/doctors/{doctor_id}/", {"name": "Other"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/doctors/{doctor_id}/").status_code, 404)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.put(f"/api/doctors/{doctor_id}/", {
            "name": "Ada Doctor", "specialization": "Neurology"
        }, format="json").status_code, 200)

    def test_mapping_assignment_read_duplicate_and_owner_deletion(self):
        patient = Patient.objects.create(owner=self.user, name="Patient")
        doctor = Doctor.objects.create(created_by=self.user, name="Doctor", specialization="Family Medicine")
        other_patient = Patient.objects.create(owner=self.other, name="Private Patient")
        other_doctor = Doctor.objects.create(created_by=self.other, name="Private Doctor", specialization="Oncology")
        other_mapping = PatientDoctorMapping.objects.create(
            patient=other_patient, doctor=other_doctor, created_by=self.other
        )
        self.client.force_authenticate(self.user)
        create = self.client.post("/api/mappings/", {"patient": patient.id, "doctor": doctor.id}, format="json")
        self.assertEqual(create.status_code, 201)
        mapping_id = create.data["id"]
        duplicate = self.client.post("/api/mappings/", {"patient": patient.id, "doctor": doctor.id}, format="json")
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(self.client.get("/api/mappings/").data["count"], 1)
        self.assertEqual(self.client.get(f"/api/mappings/{patient.id}/").data[0]["id"], doctor.id)
        self.assertNotIn("owner@example.com", str(self.client.get("/api/mappings/").data))
        self.assertEqual(self.client.get("/api/mappings/999999/").status_code, 404)
        invalid = self.client.post("/api/mappings/", {"patient": 999999, "doctor": doctor.id}, format="json")
        self.assertEqual(invalid.status_code, 400)
        self.client.force_authenticate(self.other)
        other_list = self.client.get("/api/mappings/").data
        self.assertEqual(other_list["count"], 1)
        self.assertEqual(other_list["results"][0]["id"], other_mapping.id)
        self.assertEqual(self.client.get(f"/api/mappings/{patient.id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/mappings/{mapping_id}/").status_code, 404)
        self.assertEqual(self.client.post("/api/mappings/", {"patient": patient.id, "doctor": doctor.id}, format="json").status_code, 400)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f"/api/mappings/{mapping_id}/").status_code, 204)
        self.assertFalse(PatientDoctorMapping.objects.filter(pk=mapping_id).exists())
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=other_mapping.id).exists())

    def test_doctor_delete_rejected_when_assigned(self):
        patient = Patient.objects.create(owner=self.user, name="Patient")
        doctor = Doctor.objects.create(created_by=self.user, name="Doctor", specialization="Family Medicine")
        PatientDoctorMapping.objects.create(patient=patient, doctor=doctor, created_by=self.user)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f"/api/doctors/{doctor.id}/").status_code, 409)


class HealthCheckTests(APITestCase):
    def test_health_check(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
