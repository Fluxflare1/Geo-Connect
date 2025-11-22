from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Trip
from tenancy.models import Tenant

from .serializers import (
    TripSearchRequestSerializer,
    TripSearchResponseSerializer,
    TripSummarySerializer,
)
from .services import search_trips


def get_tenant_from_request(request) -> Tenant:
    """
    Simple, explicit tenant resolution using X-Tenant header.
    You can later extend this to infer from domain, etc.
    """
    tenant_slug = request.headers.get("X-Tenant")
    if not tenant_slug:
        # For now we enforce header; you can relax/change this if you have a middleware.
        from rest_framework.exceptions import ValidationError

        raise ValidationError("X-Tenant header is required.")

    try:
        return Tenant.objects.get(slug=tenant_slug)
    except Tenant.DoesNotExist:
        from rest_framework.exceptions import ValidationError

        raise ValidationError("Invalid tenant in X-Tenant header.")


class TripSearchView(APIView):
    """
    POST /api/v1/trips/search

    Body validated by TripSearchRequestSerializer.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = get_tenant_from_request(request)
        serializer = TripSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = search_trips(tenant=tenant, validated_data=serializer.validated_data)

        # Transform TripSearchResult objects to dicts for serializer
        serialized_results = []
        for item in result["results"]:
            trip = item.trip
            route = trip.route
            origin = route.origin
            destination = route.destination
            provider = trip.provider

            serialized_results.append(
                {
                    "trip_id": trip.trip_code,
                    "provider": {
                        "id": provider.code,
                        "name": provider.name,
                        "logo_url": provider.logo_url if hasattr(provider, "logo_url") else "",
                    },
                    "mode": trip.mode,
                    "product_type": trip.product_type,
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
                    "departure_time": trip.departure_time,
                    "arrival_time": trip.arrival_time,
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
                        "vehicle_type": "",  # can be populated from route/vehicle data later
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
            trip_code=trip_id,
            is_active=True,
        )

        route = trip.route
        origin = route.origin
        destination = route.destination
        provider = trip.provider

        payload = {
            "trip_id": trip.trip_code,
            "provider": {
                "id": provider.code,
                "name": provider.name,
                "logo_url": provider.logo_url if hasattr(provider, "logo_url") else "",
            },
            "mode": trip.mode,
            "product_type": trip.product_type,
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
            "departure_time": trip.departure_time,
            "arrival_time": trip.arrival_time,
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
                "latest_change_deadline": trip.departure_time - timezone.timedelta(
                    days=1
                ),
                "latest_refund_deadline": trip.departure_time - timezone.timedelta(
                    days=1
                ),
            },
        }

        serializer = TripSummarySerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
