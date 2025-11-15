from django.db import connections
from django.db.utils import OperationalError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    GET /api/v1/health

    Lightweight – checks DB connection only.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        db_ok = True
        try:
            connections["default"].cursor()
        except OperationalError:
            db_ok = False

        if not db_ok:
            return Response(
                {"status": "unhealthy", "checks": {"database": "down"}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {"status": "ok", "checks": {"database": "up"}},
            status=status.HTTP_200_OK,
        )


class ReadinessCheckView(APIView):
    """
    GET /api/v1/readiness

    Slightly heavier – you can extend to check:
      - cache
      - message broker
      - external dependencies
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        db_ok = True
        try:
            connections["default"].cursor()
        except OperationalError:
            db_ok = False

        checks = {
            "database": "up" if db_ok else "down",
        }

        status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        overall = "ready" if db_ok else "not_ready"

        return Response(
            {
                "status": overall,
                "checks": checks,
            },
            status=status_code,
        )
