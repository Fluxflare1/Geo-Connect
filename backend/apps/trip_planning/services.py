import uuid
from datetime import time
from typing import Dict, List, Tuple

from django.db.models import F, ExpressionWrapper, DurationField
from django.utils import timezone

from apps.catalog.models import Trip, Stop
from apps.tenancy.models import Tenant


class TripSearchResult:
    """
    Simple in-memory representation used by the serializers.
    """

    def __init__(self, trip: Trip, passengers: int):
        self.trip = trip
        self.passengers = passengers

    @property
    def total_price(self):
        return self.trip.base_price * self.passengers

    @property
    def per_passenger_price(self):
        return self.trip.base_price


def _get_time_range(departure_time_str: str) -> Tuple[time | None, time | None]:
    """
    Map 'departure_time' string to a time-of-day window.

    Returns (from_time, to_time). If both are None => no time filter.
    """
    if not departure_time_str:
        return None, None

    key = departure_time_str.upper()

    if key == "ANY":
        return None, None

    if key == "MORNING":
        return time(5, 0), time(11, 59)
    if key == "AFTERNOON":
        return time(12, 0), time(17, 59)
    if key == "EVENING":
        return time(18, 0), time(22, 59)
    if key == "NIGHT":
        # For now, treat night as late-evening on that service_date
        return time(21, 0), time(23, 59)

    # Specific "HH:MM"
    try:
        hh, mm = key.split(":")
        center = time(int(hh), int(mm))
        # Approximate +/- 3 hours using simple clamps
        start_hour = max(0, center.hour - 3)
        end_hour = min(23, center.hour + 3)
        return time(start_hour, center.minute), time(end_hour, center.minute)
    except Exception:
        # Fallback: no time filter
        return None, None


def _resolve_location(tenant: Tenant, location_data: Dict, is_origin: bool) -> Stop:
    """
    Map LocationInputSerializer data to a Stop instance.

    Supports:
    - STOP_ID: Stop.code (your STOP_ID)
    - CITY_CODE: any Stop in that City (using City.code)
    - COORDINATES: nearest Stop by lat/lng
    """
    from apps.catalog.models import City  # local import to avoid cycles

    loc_type = location_data["type"]
    value = location_data["value"]

    if loc_type == "STOP_ID":
        try:
            return Stop.objects.select_related("city").get(
                tenant=tenant,
                code=value,
                active=True,
            )
        except Stop.DoesNotExist:
            raise ValueError(f"Unknown stop_id: {value}")

    if loc_type == "CITY_CODE":
        try:
            stop = (
                Stop.objects.select_related("city")
                .filter(
                    tenant=tenant,
                    city__code=value,
                    active=True,
                )
                .earliest("id")
            )
            return stop
        except Stop.DoesNotExist:
            raise ValueError(f"No stops found for city_code: {value}")

    if loc_type == "COORDINATES":
        # Expect value "lat,lng". We choose nearest active stop.
        try:
            lat_str, lng_str = value.split(",")
            lat = float(lat_str.strip())
            lng = float(lng_str.strip())
        except Exception:
            raise ValueError("Invalid coordinates format; expected 'lat,lng'.")

        qs = Stop.objects.filter(
            tenant=tenant,
            active=True,
        )
        nearest = None
        best_dist = None
        for stop in qs:
            dlat = float(stop.lat) - lat
            dlng = float(stop.lng) - lng
            dist2 = dlat * dlat + dlng * dlng
            if best_dist is None or dist2 < best_dist:
                best_dist = dist2
                nearest = stop

        if nearest is None:
            raise ValueError("No suitable stops found near given coordinates.")
        return nearest

    raise ValueError(f"Unsupported location type: {loc_type}")


def search_trips(
    tenant: Tenant,
    validated_data: Dict,
) -> Dict:
    """
    Core search logic used by TripSearchView.

    Returns a dict:
    {
      'search_id': UUID,
      'currency': 'NGN',
      'results': [TripSearchResult(...), ...]
    }
    """
    origin_loc = validated_data["origin"]
    destination_loc = validated_data["destination"]
    departure_date = validated_data["departure_date"]
    departure_time_str = validated_data.get("departure_time") or "ANY"
    passengers = validated_data.get("passengers") or 1
    mode = validated_data.get("mode") or "ANY"
    filters = validated_data.get("filters") or {}
    sort_by = validated_data.get("sort_by") or "DEPARTURE_TIME"
    sort_order = validated_data.get("sort_order") or "ASC"

    origin_stop = _resolve_location(tenant, origin_loc, is_origin=True)
    destination_stop = _resolve_location(tenant, destination_loc, is_origin=False)

    from_time, to_time = _get_time_range(departure_time_str)

    qs = (
        Trip.objects.select_related(
            "route",
            "route__origin",
            "route__destination",
            "provider",
        )
        .filter(
            tenant=tenant,
            active=True,
            route__active=True,
            service_date=departure_date,
            available_seats__gte=passengers,
            route__origin=origin_stop,
            route__destination=destination_stop,
        )
    )

    # Time-of-day filter (within the service_date)
    if from_time is not None and to_time is not None:
        qs = qs.filter(
            departure_time__gte=from_time,
            departure_time__lte=to_time,
        )

    # Filter by mode (based on route.mode)
    if mode != "ANY":
        qs = qs.filter(route__mode=mode)

    # providers filter: list of provider codes or IDs
    providers_filter = filters.get("providers") if filters else None
    if providers_filter:
        qs = qs.filter(provider__code__in=providers_filter)

    # max_price filter
    max_price = filters.get("max_price") if filters else None
    if max_price is not None:
        qs = qs.filter(base_price__lte=max_price)

    # Sorting
    if sort_by == "PRICE":
        order_field = "base_price"
    elif sort_by == "ARRIVAL_TIME":
        order_field = "arrival_time"
    elif sort_by == "DURATION":
        # Postgres: difference between time fields -> interval
        qs = qs.annotate(
            duration=ExpressionWrapper(
                F("arrival_time") - F("departure_time"),
                output_field=DurationField(),
            )
        )
        order_field = "duration"
    else:
        # DEPARTURE_TIME (default)
        order_field = "departure_time"

    if sort_order == "DESC":
        order_field = f"-{order_field}"

    qs = qs.order_by(order_field)

    results: List[TripSearchResult] = [TripSearchResult(trip, passengers) for trip in qs]

    # Decide currency: from first result or default "NGN"
    currency = "NGN"
    if results:
        currency = results[0].trip.currency

    return {
        "search_id": uuid.uuid4(),
        "currency": currency,
        "results": results,
    }
