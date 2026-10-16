from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView

from config.views import health_check
from accounts.views import LoginView, RegisterView


class TokenRefreshView(SimpleJWTTokenRefreshView):
    throttle_scope = "token_refresh"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/patients/", include("patients.urls")),
    path("api/doctors/", include("doctors.urls")),
    path("api/mappings/", include("mappings.urls")),
]
