from django.db import IntegrityError, transaction
from rest_framework import serializers

from patients.models import Patient
from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_patient(self, patient):
        if patient.owner_id != self.context["request"].user.id:
            raise serializers.ValidationError("Patient not found.")
        return patient

    def validate(self, attrs):
        patient = attrs.get("patient", getattr(self.instance, "patient", None))
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        if patient and doctor and PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError("This doctor is already assigned to this patient.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError("This doctor is already assigned to this patient.") from exc
