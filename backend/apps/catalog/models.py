import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

from apps.tenancy.models import Tenant
from apps.providers.models import Provider


class Stop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="stops")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="stops"
    )
    external_id = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    address = models.CharField(max_length=512, blank=True)
    zone = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stop"
        indexes = [
            models.Index(fields=["tenant", "provider", "external_id"]),
            models.Index(fields=["tenant", "provider", "code"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="routes")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="routes"
    )
    external_id = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    mode = models.CharField(max_length=20)  # BUS, TRAIN, FERRY, etc.
    direction = models.CharField(max_length=16, blank=True)  # OUTBOUND/INBOUND

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "route"
        indexes = [
            models.Index(fields=["tenant", "provider", "external_id"]),
            models.Index(fields=["tenant", "provider", "code"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class RouteStop(models.Model):
    """
    Ordered stops for a given route.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="route_stops")
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="route_stops")
    sequence_index = models.PositiveIntegerField()

    class Meta:
        db_table = "route_stop"
        unique_together = ("route", "stop", "sequence_index")
        ordering = ["sequence_index"]


class Trip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="trips")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="trips"
    )
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")

    external_id = models.CharField(max_length=255, blank=True)
    service_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    vehicle_type = models.CharField(max_length=64, blank=True)
    vehicle_capacity = models.PositiveIntegerField(default=0)

    operating_days = ArrayField(
        models.CharField(max_length=3), default=list, blank=True
    )  # ["MON","TUE",...]

    time_zone = models.CharField(max_length=64, default="Africa/Lagos")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trip"
        indexes = [
            models.Index(fields=["tenant", "provider", "service_date"]),
            models.Index(fields=["tenant", "provider", "external_id"]),
        ]

    def __str__(self):
        return f"{self.route.code} {self.service_date} {self.departure_time}"
