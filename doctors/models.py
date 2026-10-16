from django.conf import settings
from django.db import models


class Doctor(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_doctors")
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    clinic_address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"
