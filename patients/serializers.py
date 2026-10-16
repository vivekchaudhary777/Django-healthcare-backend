from django.utils import timezone
from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("id", "name", "date_of_birth", "gender", "email", "phone", "address", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_date_of_birth(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
