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
