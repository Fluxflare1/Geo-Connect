from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.providers.permissions import IsProviderUserOrTenantAdmin
from apps.catalog.models import Trip, Route
from .models import VehicleLocation, TripStatus, TripInventory, ServiceAlert
from .serializers import (
    VehicleLocationInputSerializer,
    TripStatusInputSerializer,
    TripInventoryInputSerializer,
    ServiceAlertInputSerializer,
)


class ProviderVehicleLocationsView(generics.GenericAPIView):
    """
    POST /api/v1/provider/vehicles/locations
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = VehicleLocationInputSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        provider = request.provider
        vehicles = request.data.get("vehicles", [])

        serializer = self.get_serializer(data=vehicles, many=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        created = 0

        for v in data:
            trip = None
            trip_id = v.get("trip_id")
            if trip_id:
                try:
                    trip = Trip.objects.get(id=trip_id, tenant=tenant, provider=provider)
                except Trip.DoesNotExist:
                    trip = None

            occupancy = v.get("occupancy") or {}
            VehicleLocation.objects.create(
                tenant=tenant,
                provider=provider,
                trip=trip,
                vehicle_id=v["vehicle_id"],
                lat=v["lat"],
                lng=v["lng"],
                speed_kmh=v.get("speed_kmh"),
                heading_deg=v.get("heading_deg"),
                occupancy_capacity=occupancy.get("capacity", 0),
                occupancy_taken=occupancy.get("seats_taken", 0),
                status=v.get("status", "IN_SERVICE"),
                recorded_at=v["timestamp"],
            )
            created += 1

        return Response({"accepted": created, "failed": 0}, status=status.HTTP_202_ACCEPTED)


class ProviderTripStatusView(generics.GenericAPIView):
    """
    POST /api/v1/provider/trips/status
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = TripStatusInputSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        provider = request.provider
        updates = request.data.get("updates", [])

        serializer = self.get_serializer(data=updates, many=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        applied = 0
        errors = []

        for u in data:
            try:
                trip = Trip.objects.get(id=u["trip_id"], tenant=tenant, provider=provider)
            except Trip.DoesNotExist:
                errors.append({"trip_id": str(u["trip_id"]), "error": "TRIP_NOT_FOUND"})
                continue

            ts, _ = TripStatus.objects.update_or_create(
                tenant=tenant,
                provider=provider,
                trip=trip,
                defaults={
                    "status": u["status"],
                    "delay_minutes": u.get("delay_minutes", 0),
                    "reason_code": u.get("reason_code", ""),
                },
            )
            applied += 1

        return Response({"applied": applied, "errors": errors}, status=status.HTTP_200_OK)


class ProviderTripInventoryView(generics.GenericAPIView):
    """
    POST /api/v1/provider/trips/inventory
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = TripInventoryInputSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        provider = request.provider
        payload = request.data.get("inventory", [])

        serializer = self.get_serializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        applied = 0
        errors = []

        for inv in data:
            try:
                trip = Trip.objects.get(
                    id=inv["trip_id"],
                    tenant=tenant,
                    provider=provider,
                )
            except Trip.DoesNotExist:
                errors.append({"trip_id": str(inv["trip_id"]), "error": "TRIP_NOT_FOUND"})
                continue

            TripInventory.objects.update_or_create(
                tenant=tenant,
                provider=provider,
                trip=trip,
                service_date=inv["service_date"],
                defaults={
                    "seats_total": inv["seats_total"],
                    "seats_available": inv["seats_available"],
                },
            )
            applied += 1

        return Response({"applied": applied, "errors": errors}, status=status.HTTP_200_OK)


class ProviderServiceAlertsView(generics.GenericAPIView):
    """
    POST /api/v1/provider/service-alerts
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = ServiceAlertInputSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        provider = request.provider
        alerts = request.data.get("alerts", [])

        serializer = self.get_serializer(data=alerts, many=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        applied = 0
        errors = []

        for a in data:
            alert, _ = ServiceAlert.objects.update_or_create(
                tenant=tenant,
                provider=provider,
                external_id=a["id"],
                defaults={
                    "severity": a["severity"],
                    "type": a["type"],
                    "title": a["title"],
                    "description": a.get("description", ""),
                    "actions": a.get("actions", []),
                    "affected_from": a["affected_from"],
                    "affected_until": a["affected_until"],
                },
            )
            route_ids = a.get("route_ids") or []
            if route_ids:
                routes = Route.objects.filter(id__in=route_ids, tenant=tenant, provider=provider)
                alert.routes.set(routes)

            applied += 1

        return Response({"applied": applied, "errors": errors}, status=status.HTTP_200_OK)
