from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Doctor
from .serializers import DoctorSerializer


class DoctorInUse(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This doctor is assigned to one or more patients and cannot be deleted."
    default_code = "doctor_in_use"


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Authenticated users may discover all doctors; only creators may change them.
        queryset = Doctor.objects.all()
        if self.action in {"update", "partial_update", "destroy"}:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError as exc:
            raise DoctorInUse() from exc
        return Response(status=status.HTTP_204_NO_CONTENT)
