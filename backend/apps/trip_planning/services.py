import uuid
from datetime import datetime, time, timedelta
from typing import Dict, List, Tuple

from django.db.models import Q
from django.utils import timezone

from catalog.models import Trip, TravelMode, ProductType, Stop
from tenancy.models import Tenant


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


def _parse_time_window(departure_date, departure_time_str) -> Tuple[datetime, datetime]:
    """
    Map 'departure_time' string to a time window on that date.
    """
    local_tz = timezone.get_current_timezone()

    if not departure_time_str or departure_time_str.upper() == "ANY":
        start = datetime.combine(departure_date, time.min)
        end = datetime.combine(departure_date, time.max)
    else:
        key = departure_time_str.upper()
        if key == "MORNING":
            start = datetime.combine(departure_date, time(5, 0))
            end = datetime.combine(departure_date, time(11, 59))
        elif key == "AFTERNOON":
            start = datetime.combine(departure_date, time(12, 0))
            end = datetime.combine(departure_date, time(17, 59))
        elif key == "EVENING":
            start = datetime.combine(departure_date, time(18, 0))
            end = datetime.combine(departure_date, time(22, 59))
        elif key == "NIGHT":
            start = datetime.combine(departure_date, time(23, 0))
            end = datetime.combine(departure_date + timedelta(days=1), time(4, 59))
        else:
            # Specific "HH:MM" time – we look at +/- 3 hours window
            try:
                hh, mm = departure_time_str.split(":")
                base = datetime.combine(departure_date, time(int(hh), int(mm)))
                start = base - timedelta(hours=3)
                end = base + timedelta(hours=3)
            except Exception:  # noqa
                start = datetime.combine(departure_date, time.min)
                end = datetime.combine(departure_date, time.max)

    start = local_tz.localize(start)
    end = local_tz.localize(end)
    return start, end


def _resolve_location(tenant: Tenant, location_data: Dict, is_origin: bool) -> Stop:
    """
    Map LocationInputSerializer data to a Stop instance.
    Currently implements STOP_ID and CITY_CODE. COORDINATES can be extended later.
    """
    loc_type = location_data["type"]
    value = location_data["value"]

    if loc_type == "STOP_ID":
        try:
            return Stop.objects.select_related("city").get(
                tenant=tenant, code=value, is_active=True
            )
        except Stop.DoesNotExist:
            raise ValueError(f"Unknown stop_id: {value}")

    if loc_type == "CITY_CODE":
        # For city-based search, we pick any stop in the city as a representative origin.
        # The search will then filter by city on routes.
        try:
            stop = (
                Stop.objects.select_related("city")
                .filter(
                    tenant=tenant,
                    city__code=value,
                    is_active=True,
                )
                .earliest("id")
            )
            return stop
        except Stop.DoesNotExist:
            raise ValueError(f"No stops found for city_code: {value}")

    if loc_type == "COORDINATES":
        # Expect value "lat,lng". For now we approximate by nearest active stop.
        try:
            lat_str, lng_str = value.split(",")
            lat = float(lat_str.strip())
            lng = float(lng_str.strip())
        except Exception:
            raise ValueError("Invalid coordinates format; expected 'lat,lng'.")

        qs = Stop.objects.filter(tenant=tenant, is_active=True, latitude__isnull=False)
        # Simple linear scan; for large datasets, use PostGIS or similar.
        nearest = None
        best_dist = None
        for stop in qs:
            if stop.latitude is None or stop.longitude is None:
                continue
            dlat = float(stop.latitude) - lat
            dlng = float(stop.longitude) - lng
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
    Returns a dict: { 'search_id': UUID, 'currency': 'NGN', 'results': [TripSearchResult...] }
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

    start_dt, end_dt = _parse_time_window(departure_date, departure_time_str)

    qs = (
        Trip.objects.select_related("route", "route__origin", "route__destination", "provider")
        .filter(
            tenant=tenant,
            is_active=True,
            route__is_active=True,
            departure_time__gte=start_dt,
            departure_time__lte=end_dt,
            available_seats__gte=passengers,
        )
    )

    # Filter by mode
    if mode != "ANY":
        qs = qs.filter(mode=mode)

    # Filter by route origin/destination
    qs = qs.filter(
        route__origin=origin_stop,
        route__destination=destination_stop,
    )

    # Filters.providers: provider IDs/codes.
    providers_filter = filters.get("providers") if filters else None
    if providers_filter:
        qs = qs.filter(provider__code__in=providers_filter)

    # filters.max_price
    max_price = filters.get("max_price") if filters else None
    if max_price is not None:
        qs = qs.filter(base_price__lte=max_price)

    # filters.direct_only – for now all trips are direct.
    # If multi-leg is introduced, apply additional constraints here.

    # Sorting
    if sort_by == "PRICE":
        order_field = "base_price"
    elif sort_by == "ARRIVAL_TIME":
        order_field = "arrival_time"
    elif sort_by == "DURATION":
        order_field = "arrival_time__minus_departure"  # can't order by property; handle via annotation if needed
    else:
        order_field = "departure_time"

    if sort_by == "DURATION":
        from django.db.models import ExpressionWrapper, DurationField, F

        qs = qs.annotate(
            duration=ExpressionWrapper(
                F("arrival_time") - F("departure_time"),
                output_field=DurationField(),
            )
        )
        order_field = "duration"

    if sort_order == "DESC":
        order_field = f"-{order_field}"

    qs = qs.order_by(order_field)

    # Collect search results
    results: List[TripSearchResult] = [TripSearchResult(trip, passengers) for trip in qs]

    # Decide currency (for now from first result, default NGN if none).
    currency = "NGN"
    if results:
        currency = results[0].trip.currency

    return {
        "search_id": uuid.uuid4(),
        "currency": currency,
        "results": results,
    }
