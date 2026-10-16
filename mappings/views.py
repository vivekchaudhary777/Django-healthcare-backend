from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import MappingSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(patient__owner=self.request.user).select_related("patient", "doctor")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDoctorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id, owner=request.user)
        doctors = Doctor.objects.filter(patient_mappings__patient=patient).order_by("id").distinct()
        return Response(DoctorSerializer(doctors, many=True).data)

    def delete(self, request, patient_id):
        mapping = get_object_or_404(PatientDoctorMapping, pk=patient_id, patient__owner=request.user)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
