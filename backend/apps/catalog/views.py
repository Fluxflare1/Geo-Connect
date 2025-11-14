from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.providers.permissions import IsProviderUserOrTenantAdmin
from .models import Stop, Route, Trip
from .serializers import StopSerializer, RouteSerializer, TripSerializer


# ---------- PROVIDER BULK ENDPOINTS ----------


class ProviderStopsBulkUpsertView(generics.GenericAPIView):
    """
    POST /api/v1/provider/stops

    Body:
    {
      "stops": [ { ... }, ... ]
    }
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = StopSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        provider = request.provider
        stops_payload = request.data.get("stops", [])

        created = 0
        updated = 0
        result = []

        for s in stops_payload:
            external_id = s.get("external_id")
            defaults = {
                "tenant": tenant,
                "provider": provider,
                "code": s.get("code", ""),
                "name": s["name"],
                "lat": s["lat"],
                "lng": s["lng"],
                "address": s.get("address", ""),
                "zone": s.get("zone", ""),
                "active": s.get("active", True),
            }
            obj, is_created = Stop.objects.update_or_create(
                tenant=tenant,
                provider=provider,
                external_id=external_id,
                defaults=defaults,
            )
            if is_created:
                created += 1
            else:
                updated += 1
            result.append({"id": str(obj.id), "external_id": external_id, "code": obj.code})

        return Response(
            {"created": created, "updated": updated, "stops": result},
            status=status.HTTP_200_OK,
        )


class ProviderRoutesBulkUpsertView(generics.GenericAPIView):
    """
    POST /api/v1/provider/routes

    Body:
    {
      "routes": [
        {
          "external_id": "...",
          "code": "JIB-LEK",
          "name": "...",
          "mode": "BUS",
          "direction": "OUTBOUND",
          "stops_sequence": ["<stop_uuid1>", "<stop_uuid2>", ...]
        }
      ]
    }
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = RouteSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        provider = request.provider
        routes_payload = request.data.get("routes", [])

        created = 0
        updated = 0
        result = []

        for r in routes_payload:
            external_id = r.get("external_id")
            stops_sequence = r.get("stops_sequence", [])
            defaults = {
                "tenant": tenant,
                "provider": provider,
                "code": r["code"],
                "name": r["name"],
                "mode": r["mode"],
                "direction": r.get("direction", ""),
                "active": r.get("active", True),
            }
            route, is_created = Route.objects.update_or_create(
                tenant=tenant,
                provider=provider,
                external_id=external_id,
                defaults=defaults,
            )
            # update stops sequence
            from .models import RouteStop, Stop

            RouteStop.objects.filter(route=route).delete()
            for idx, stop_id in enumerate(stops_sequence):
                RouteStop.objects.create(
                    route=route,
                    stop=Stop.objects.get(id=stop_id, tenant=tenant, provider=provider),
                    sequence_index=idx,
                )

            if is_created:
                created += 1
            else:
                updated += 1
            result.append(
                {
                    "id": str(route.id),
                    "external_id": external_id,
                    "code": route.code,
                }
            )

        return Response(
            {"created": created, "updated": updated, "routes": result},
            status=status.HTTP_200_OK,
        )


class ProviderTripsBulkUpsertView(generics.GenericAPIView):
    """
    POST /api/v1/provider/trips

    Body:
    {
      "trips": [ { ... }, ... ]
    }
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = TripSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        provider = request.provider
        trips_payload = request.data.get("trips", [])

        created = 0
        updated = 0
        result = []

        for t in trips_payload:
            external_id = t.get("external_id")
            route_id = t["route_id"]

            defaults = {
                "tenant": tenant,
                "provider": provider,
                "route_id": route_id,
                "service_date": t["service_date"],
                "departure_time": t["departure_time"],
                "arrival_time": t["arrival_time"],
                "vehicle_type": t.get("vehicle_type", ""),
                "vehicle_capacity": t.get("vehicle_capacity", 0),
                "operating_days": t.get("operating_days", []),
                "time_zone": t.get("time_zone", "Africa/Lagos"),
            }

            trip, is_created = Trip.objects.update_or_create(
                tenant=tenant,
                provider=provider,
                external_id=external_id,
                defaults=defaults,
            )

            if is_created:
                created += 1
            else:
                updated += 1

            result.append(
                {
                    "id": str(trip.id),
                    "external_id": external_id,
                    "route_id": str(trip.route_id),
                }
            )

        return Response(
            {"created": created, "updated": updated, "trips": result},
            status=status.HTTP_200_OK,
        )


# ---------- READ-ONLY CATALOG ENDPOINTS ----------


class StopListView(generics.ListAPIView):
    """
    GET /api/v1/catalog/stops
    """
    permission_classes = [IsAuthenticated]  # can adjust later for public read
    serializer_class = StopSerializer

    def get_queryset(self):
        tenant = self.request.tenant
        qs = Stop.objects.filter(tenant=tenant, active=True)
        provider_id = self.request.query_params.get("provider_id")
        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        return qs.order_by("name")


class RouteListView(generics.ListAPIView):
    """
    GET /api/v1/catalog/routes
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RouteSerializer

    def get_queryset(self):
        tenant = self.request.tenant
        qs = Route.objects.filter(tenant=tenant, active=True)
        provider_id = self.request.query_params.get("provider_id")
        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        mode = self.request.query_params.get("mode")
        if mode:
            qs = qs.filter(mode=mode)
        return qs.order_by("name")


class TripListView(generics.ListAPIView):
    """
    GET /api/v1/catalog/trips
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TripSerializer

    def get_queryset(self):
        tenant = self.request.tenant
        qs = Trip.objects.filter(tenant=tenant)
        provider_id = self.request.query_params.get("provider_id")
        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        service_date = self.request.query_params.get("service_date")
        if service_date:
            qs = qs.filter(service_date=service_date)
        route_id = self.request.query_params.get("route_id")
        if route_id:
            qs = qs.filter(route_id=route_id)
        return qs.order_by("service_date", "departure_time")
