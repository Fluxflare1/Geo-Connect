from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Trip
from apps.tenancy.models import Tenant

from .serializers import (
    TripSearchRequestSerializer,
    TripSearchResponseSerializer,
    TripSummarySerializer,
)
from .services import search_trips


def get_tenant_from_request(request) -> Tenant:
    """
    Simple, explicit tenant resolution using X-Tenant header.

    You can extend this later to infer from domain or JWT claims if needed.
    """
    from rest_framework.exceptions import ValidationError

    tenant_slug = request.headers.get("X-Tenant")
    if not tenant_slug:
        raise ValidationError("X-Tenant header is required.")

    try:
        return Tenant.objects.get(slug=tenant_slug)
    except Tenant.DoesNotExist:
        raise ValidationError("Invalid tenant in X-Tenant header.")


class TripSearchView(APIView):
    """
    POST /api/v1/trips/search
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = get_tenant_from_request(request)

        serializer = TripSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = search_trips(tenant=tenant, validated_data=serializer.validated_data)

        serialized_results = []
        for item in result["results"]:
            trip = item.trip
            route = trip.route
            origin = route.origin
            destination = route.destination
            provider = trip.provider

            serialized_results.append(
                {
                    "trip_id": str(trip.id),
                    "provider": {
                        "id": provider.code,
                        "name": provider.name,
                        "logo_url": getattr(provider, "logo_url", "") or "",
                    },
                    "mode": route.mode,
                    "product_type": route.product_type,
                    "origin": {
                        "stop_id": origin.code,
                        "name": origin.name,
                        "city_code": origin.city.code if origin.city else "",
                    },
                    "destination": {
                        "stop_id": destination.code,
                        "name": destination.name,
                        "city_code": destination.city.code if destination.city else "",
                    },
                    "departure_time": trip.departure_datetime,
                    "arrival_time": trip.arrival_datetime,
                    "duration_minutes": trip.duration_minutes,
                    "available_seats": trip.available_seats,
                    "price": {
                        "currency": trip.currency,
                        "total": item.total_price,
                        "per_passenger": item.per_passenger_price,
                        "fees_included": True,
                    },
                    "constraints": {
                        "refundable": True,
                        "changeable": True,
                        "baggage_included": True,
                        "checkin_required": False,
                    },
                    "tags": [],
                    "preview": {
                        "vehicle_type": trip.vehicle_type or "",
                        "route_label": f"{origin.name} → {destination.name}",
                        "badge": "",
                        "primary_color": "",
                    },
                }
            )

        response_payload = {
            "search_id": result["search_id"],
            "currency": result["currency"],
            "results": serialized_results,
        }

        response_serializer = TripSearchResponseSerializer(response_payload)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class TripSummaryView(APIView):
    """
    GET /api/v1/trips/{trip_id}/summary
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, trip_id: str):
        tenant = get_tenant_from_request(request)

        trip = get_object_or_404(
            Trip.objects.select_related(
                "route",
                "route__origin",
                "route__destination",
                "provider",
            ),
            tenant=tenant,
            id=trip_id,
            active=True,
        )

        route = trip.route
        origin = route.origin
        destination = route.destination
        provider = trip.provider

        latest_deadline = trip.departure_datetime - timedelta(days=1)

        payload = {
            "trip_id": str(trip.id),
            "provider": {
                "id": provider.code,
                "name": provider.name,
                "logo_url": getattr(provider, "logo_url", "") or "",
            },
            "mode": route.mode,
            "product_type": route.product_type,
            "origin": {
                "stop_id": origin.code,
                "name": origin.name,
                "city_code": origin.city.code if origin.city else "",
            },
            "destination": {
                "stop_id": destination.code,
                "name": destination.name,
                "city_code": destination.city.code if destination.city else "",
            },
            "departure_time": trip.departure_datetime,
            "arrival_time": trip.arrival_datetime,
            "duration_minutes": trip.duration_minutes,
            "available_seats": trip.available_seats,
            "currency": trip.currency,
            "total_price": trip.base_price,
            "per_passenger_price": trip.base_price,
            "fare_rules": {
                "refundable": True,
                "changeable": True,
                "refund_penalty_percent": 10,
                "change_penalty_percent": 5,
                "latest_change_deadline": latest_deadline,
                "latest_refund_deadline": latest_deadline,
            },
        }

        serializer = TripSummarySerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
