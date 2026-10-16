from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


def health_check(request):
    try:
        connections["default"].ensure_connection()
    except OperationalError:
        return JsonResponse({"status": "unhealthy", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "connected"})
