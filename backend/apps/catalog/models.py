import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

from apps.tenancy.models import Tenant
from apps.providers.models import Provider


# ---------------------------
# Enums
# ---------------------------

class TravelMode(models.TextChoices):
    BUS = "BUS", "Bus / Coach"
    RAIL = "RAIL", "Rail"
    FERRY = "FERRY", "Ferry / Boat"
    TAXI = "TAXI", "Taxi / Ride-hailing"
    SHUTTLE = "SHUTTLE", "Shuttle / Minibus"
    OTHER = "OTHER", "Other"


class ProductType(models.TextChoices):
    INTERCITY = "INTERCITY", "Intercity"
    CITY_BUS = "CITY_BUS", "City Bus"
    RIDE_HAIL = "RIDE_HAIL", "Ride-hailing"
    SCHOOL = "SCHOOL", "School Transport"
    CORPORATE = "CORPORATE", "Corporate Shuttle"
    OTHER = "OTHER", "Other"


# ---------------------------
# City
# ---------------------------

class City(models.Model):
    """
    Helper for grouping stops/terminals by city for search and reporting.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="cities",
    )
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "city"
        unique_together = ("tenant", "code")
        indexes = [
            models.Index(fields=["tenant", "code"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


# ---------------------------
# Stop
# ---------------------------

class Stop(models.Model):
    """
    A stop, station, or terminal where trips start/end.

    This merges the original Stop with the extended search-related fields.
    - `code` is the STOP_ID used by APIs (e.g. "lagos-jibowu-terminal").
    - `lat` / `lng` are kept (existing schema).
    - `city` is added to support CITY_CODE-based search.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="stops")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="stops"
    )

    external_id = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=64, blank=True)  # STOP_ID (kept but widened)
    name = models.CharField(max_length=255)

    # City grouping (new)
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stops",
    )

    # Coordinates (keep existing lat/lng naming)
    lat = models.FloatField()
    lng = models.FloatField()

    address = models.CharField(max_length=512, blank=True)
    zone = models.CharField(max_length=64, blank=True)

    # Activity flag (existing)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stop"
        indexes = [
            # Original indexes
            models.Index(fields=["tenant", "provider", "external_id"]),
            models.Index(fields=["tenant", "provider", "code"]),
            # Extra indexes (useful for search)
            models.Index(fields=["tenant", "code"]),
            models.Index(fields=["tenant", "provider"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ---------------------------
# Route
# ---------------------------

class Route(models.Model):
    """
    A logical route operated by a provider.

    This merges:
    - Original Route (UUID PK, external_id, code, name, mode, direction, active)
    - Extended Route (origin, destination, product_type, estimated_duration_minutes)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="routes")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="routes"
    )

    external_id = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=255)

    # Mode with choices (extends original simple CharField)
    mode = models.CharField(
        max_length=20,  # keep original max_length
        choices=TravelMode.choices,
        default=TravelMode.BUS,
    )

    # OUTBOUND / INBOUND etc.
    direction = models.CharField(max_length=16, blank=True)

    # New: product type (intercity, city bus, etc.)
    product_type = models.CharField(
        max_length=32,
        choices=ProductType.choices,
        default=ProductType.INTERCITY,
    )

    # New: endpoints of the route
    origin = models.ForeignKey(
        Stop,
        on_delete=models.PROTECT,
        related_name="origin_routes",
        null=True,
        blank=True,
    )
    destination = models.ForeignKey(
        Stop,
        on_delete=models.PROTECT,
        related_name="destination_routes",
        null=True,
        blank=True,
    )

    # New: optional cached duration in minutes
    estimated_duration_minutes = models.PositiveIntegerField(default=0)

    # Existing activity flag
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "route"
        unique_together = ("tenant", "provider", "code")
        indexes = [
            # Original
            models.Index(fields=["tenant", "provider", "external_id"]),
            models.Index(fields=["tenant", "provider", "code"]),
            # Extra for search
            models.Index(fields=["tenant", "mode"]),
            models.Index(fields=["tenant", "origin"]),
            models.Index(fields=["tenant", "destination"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


# ---------------------------
# RouteStop
# ---------------------------

class RouteStop(models.Model):
    """
    Ordered stops for a given route.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="route_stops"
    )
    stop = models.ForeignKey(
        Stop, on_delete=models.CASCADE, related_name="route_stops"
    )
    sequence_index = models.PositiveIntegerField()

    class Meta:
        db_table = "route_stop"
        unique_together = ("route", "stop", "sequence_index")
        ordering = ["sequence_index"]

    def __str__(self) -> str:
        return f"{self.route.code} #{self.sequence_index} - {self.stop.name}"


# ---------------------------
# Trip
# ---------------------------

class Trip(models.Model):
    """
    A scheduled trip (single departure) along a route.

    This merges:
    - Your existing GTFS-like structure (service_date + departure_time/arrival_time, operating_days, time_zone)
    - Pricing/capacity fields needed by the booking engine & search.

    We keep:
    - id (UUID PK)
    - tenant, provider, route
    - service_date, departure_time, arrival_time
    - vehicle_type, vehicle_capacity
    - operating_days, time_zone

    We add:
    - currency, base_price, available_seats
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="trips")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="trips"
    )
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")

    external_id = models.CharField(max_length=255, blank=True)

    # Service date and times (existing)
    service_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    vehicle_type = models.CharField(max_length=64, blank=True)
    vehicle_capacity = models.PositiveIntegerField(default=0)

    operating_days = ArrayField(
        models.CharField(max_length=3), default=list, blank=True
    )  # ["MON","TUE",...]

    time_zone = models.CharField(max_length=64, default="Africa/Lagos")

    # Pricing & inventory (new)
    currency = models.CharField(max_length=8, default="NGN")
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available_seats = models.PositiveIntegerField(default=0)

    # Optional "active" flag for this specific trip instance
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trip"
        indexes = [
            models.Index(fields=["tenant", "provider", "service_date"]),
            models.Index(fields=["tenant", "provider", "external_id"]),
            models.Index(fields=["tenant", "route"]),
        ]

    def __str__(self):
        return f"{self.route.code} {self.service_date} {self.departure_time}"

    # -----------------------
    # Helper properties
    # -----------------------

    @property
    def departure_datetime(self):
        """
        Combine service_date + departure_time into a timezone-aware datetime.
        """
        from datetime import datetime
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(self.time_zone)
        dt = datetime.combine(self.service_date, self.departure_time)
        return dt.replace(tzinfo=tz)

    @property
    def arrival_datetime(self):
        """
        Combine service_date + arrival_time into a timezone-aware datetime.
        NOTE: For overnight trips, you might need logic to add +1 day.
        """
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(self.time_zone)
        dt = datetime.combine(self.service_date, self.arrival_time)
        # TODO (later): handle overnight trips explicitly.
        return dt.replace(tzinfo=tz)

    @property
    def duration_minutes(self) -> int:
        """
        Duration of this trip in minutes, based on departure/arrival datetimes.
        """
        delta = self.arrival_datetime - self.departure_datetime
        return max(0, int(delta.total_seconds() // 60))

    def is_future(self) -> bool:
        """
        True if the trip has not yet departed (based on departure_datetime).
        """
        return self.departure_datetime >= timezone.now()
