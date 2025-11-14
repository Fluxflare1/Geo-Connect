import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

from apps.tenancy.models import Tenant
from apps.providers.models import Provider
from apps.catalog.models import Trip, Route


class VehicleLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="vehicle_locations")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="vehicle_locations")
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicle_locations")

    vehicle_id = models.CharField(max_length=64)
    lat = models.FloatField()
    lng = models.FloatField()
    speed_kmh = models.FloatField(null=True, blank=True)
    heading_deg = models.FloatField(null=True, blank=True)

    occupancy_capacity = models.PositiveIntegerField(default=0)
    occupancy_taken = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=32,
        default="IN_SERVICE",
        help_text="IN_SERVICE, OUT_OF_SERVICE, AT_DEPOT, etc",
    )

    # timestamp of the location sample
    recorded_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_location"
        indexes = [
            models.Index(fields=["tenant", "provider", "vehicle_id", "recorded_at"]),
            models.Index(fields=["tenant", "provider", "trip", "recorded_at"]),
        ]


class TripStatus(models.Model):
    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("BOARDING", "Boarding"),
        ("IN_PROGRESS", "In progress"),
        ("DELAYED", "Delayed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="trip_statuses")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="trip_statuses")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="statuses")

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="SCHEDULED")
    delay_minutes = models.IntegerField(default=0)
    reason_code = models.CharField(max_length=64, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trip_status"
        indexes = [
            models.Index(fields=["tenant", "provider", "trip"]),
        ]

  class TripInventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="trip_inventories")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="trip_inventories")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="inventory")

    service_date = models.DateField()
    seats_total = models.PositiveIntegerField(default=0)
    seats_available = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trip_inventory"
        unique_together = ("tenant", "provider", "trip", "service_date")
        indexes = [
            models.Index(fields=["tenant", "provider", "service_date"]),
        ]


class ServiceAlert(models.Model):
    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    TYPE_CHOICES = [
        ("ROUTE_DISRUPTION", "Route disruption"),
        ("CANCELLATION", "Cancellation"),
        ("DELAY", "Delay"),
        ("INFO", "Information"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="service_alerts")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="service_alerts", null=True, blank=True
    )
    routes = models.ManyToManyField(Route, related_name="service_alerts", blank=True)

    external_id = models.CharField(max_length=255, blank=True)

    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    actions = ArrayField(models.CharField(max_length=32), default=list, blank=True)

    affected_from = models.DateTimeField()
    affected_until = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_alert"
        indexes = [
            models.Index(fields=["tenant", "severity", "type"]),
        ]


