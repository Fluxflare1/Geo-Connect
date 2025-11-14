from rest_framework import serializers
from .models import VehicleLocation, TripStatus, TripInventory, ServiceAlert


class VehicleLocationInputSerializer(serializers.Serializer):
    vehicle_id = serializers.CharField(max_length=64)
    trip_id = serializers.UUIDField(required=False)
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    speed_kmh = serializers.FloatField(required=False, allow_null=True)
    heading_deg = serializers.FloatField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField()
    occupancy = serializers.DictField(required=False)
    status = serializers.CharField(max_length=32, required=False)


class TripStatusInputSerializer(serializers.Serializer):
    trip_id = serializers.UUIDField()
    status = serializers.ChoiceField(
        choices=["SCHEDULED", "BOARDING", "IN_PROGRESS", "DELAYED", "COMPLETED", "CANCELLED"]
    )
    delay_minutes = serializers.IntegerField(required=False)
    reason_code = serializers.CharField(max_length=64, required=False, allow_blank=True)
    updated_at = serializers.DateTimeField(required=False)

class TripInventoryInputSerializer(serializers.Serializer):
    trip_id = serializers.UUIDField()
    service_date = serializers.DateField()
    seats_total = serializers.IntegerField()
    seats_available = serializers.IntegerField()
    updated_at = serializers.DateTimeField(required=False)


class ServiceAlertInputSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    severity = serializers.ChoiceField(choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    type = serializers.ChoiceField(
        choices=["ROUTE_DISRUPTION", "CANCELLATION", "DELAY", "INFO"]
    )
    route_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True
    )
    affected_from = serializers.DateTimeField()
    affected_until = serializers.DateTimeField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    actions = serializers.ListField(
        child=serializers.CharField(max_length=32), required=False, allow_empty=True
    )

