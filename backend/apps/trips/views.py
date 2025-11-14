from datetime import datetime
from typing import Optional

from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.catalog.models import Trip, RouteStop
from apps.pricing.services import calculate_fare_for_trip

from apps.realtime.models import TripStatus, TripInventory


class TripSearchView(generics.GenericAPIView):
    """
    GET /api/v1/trips/search

    Query params:
      origin_lat, origin_lng (required)
      dest_lat, dest_lng (required)
      departure_time or arrival_time (ISO8601)
      mode (optional)
      provider_id (optional)
      limit, offset

    For Phase 3 we support simple single-leg trips (no transfers).
    """

    permission_classes = [AllowAny]  # public search is allowed

    def get(self, request, *args, **kwargs):
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return Response(
                {
                    "error": {
                        "code": "TENANT_REQUIRED",
                        "message": "Tenant context is required for trip search.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            origin_lat = float(request.query_params["origin_lat"])
            origin_lng = float(request.query_params["origin_lng"])
            dest_lat = float(request.query_params["dest_lat"])
            dest_lng = float(request.query_params["dest_lng"])
        except (KeyError, ValueError):
            return Response(
                {
                    "error": {
                        "code": "INVALID_COORDS",
                        "message": "origin_lat, origin_lng, dest_lat, dest_lng are required and must be numeric.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        departure_time_str = request.query_params.get("departure_time")
        arrival_time_str = request.query_params.get("arrival_time")

        if not departure_time_str and not arrival_time_str:
            return Response(
                {
                    "error": {
                        "code": "TIME_REQUIRED",
                        "message": "Either departure_time or arrival_time must be provided.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # For now we treat only departure_time-based search.
        service_date = None
        if departure_time_str:
            dt = parse_datetime(departure_time_str)
            if dt is None:
                return Response(
                    {
                        "error": {
                            "code": "INVALID_DEPARTURE_TIME",
                            "message": "departure_time must be ISO8601.",
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if dt.tzinfo is None:
                dt = make_aware(dt)
            service_date = dt.date()
        elif arrival_time_str:
            dt = parse_datetime(arrival_time_str)
            if dt is None:
                return Response(
                    {
                        "error": {
                            "code": "INVALID_ARRIVAL_TIME",
                            "message": "arrival_time must be ISO8601.",
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if dt.tzinfo is None:
                dt = make_aware(dt)
            service_date = dt.date()

        mode = request.query_params.get("mode")
        provider_id = request.query_params.get("provider_id")
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))

        qs = Trip.objects.select_related("route", "provider", "tenant").filter(
            tenant=tenant, service_date=service_date
        )

        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        if mode:
            qs = qs.filter(route__mode=mode)

        qs = qs.order_by("departure_time")[offset : offset + limit]

        trips_data = []
        for trip in qs:
            segments = self._build_segments_for_trip(trip)
            if not segments:
                continue  # skip malformed routes

            fare_info = calculate_fare_for_trip(
                trip=trip,
                origin_lat=origin_lat,
                origin_lng=origin_lng,
                dest_lat=dest_lat,
                dest_lng=dest_lng,
                mode=trip.route.mode,
            )

            trips_data.append(
                {
                    "id": str(trip.id),
                    "provider_id": str(trip.provider_id),
                    "provider_name": trip.provider.name,
                    "mode": trip.route.mode.upper(),
                    "segments": segments,
                    "duration_minutes": self._estimate_duration_minutes(trip),
                    "total_distance_km": fare_info["distance_km"],
                    "fare_estimate": {
                        "currency": fare_info["currency"],
                        "amount": fare_info["amount"],
                        "components": fare_info["components"],
                    },
                    "availability": {
                        # real-time seats will come later (Phase 5)
                        "seats_total": trip.vehicle_capacity,
                        "seats_available": trip.vehicle_capacity,  # placeholder until inventory integration
                    },
                }
            )

        return Response(
            {
                "trips": trips_data,
                "meta": {
                    "limit": limit,
                    "offset": offset,
                    "total": None,  # can add count later if needed
                },
            },
            status=status.HTTP_200_OK,
        )

    def _build_segments_for_trip(self, trip) -> Optional[list]:
        route_stops = (
            RouteStop.objects.select_related("stop")
            .filter(route=trip.route)
            .order_by("sequence_index")
        )
        if not route_stops.exists():
            return None

        first = route_stops.first().stop
        last = route_stops.last().stop

        departure_dt = datetime.combine(trip.service_date, trip.departure_time)
        arrival_dt = datetime.combine(trip.service_date, trip.arrival_time)

        return [
            {
                "segment_id": f"seg_{trip.id}",
                "from_stop": {
                    "id": str(first.id),
                    "name": first.name,
                    "lat": first.lat,
                    "lng": first.lng,
                },
                "to_stop": {
                    "id": str(last.id),
                    "name": last.name,
                    "lat": last.lat,
                    "lng": last.lng,
                },
                "departure_time": departure_dt.isoformat() + "Z",
                "arrival_time": arrival_dt.isoformat() + "Z",
                "vehicle_type": trip.vehicle_type or "",
                "real_time_status": {
                    "delay_minutes": 0,
                    "status": "ON_TIME",
                },
            }
        ]

    def _estimate_duration_minutes(self, trip) -> int:
        dt_dep = datetime.combine(trip.service_date, trip.departure_time)
        dt_arr = datetime.combine(trip.service_date, trip.arrival_time)
        diff = dt_arr - dt_dep
        return int(diff.total_seconds() // 60)
