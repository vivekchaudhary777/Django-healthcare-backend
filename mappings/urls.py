from django.urls import path
from .views import MappingListCreateView, PatientDoctorListView

urlpatterns = [
    path("", MappingListCreateView.as_view(), name="mapping-list-create"),
    path("<int:patient_id>/", PatientDoctorListView.as_view(), name="patient-doctors-mapping-delete"),
]
