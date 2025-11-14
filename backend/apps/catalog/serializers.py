from rest_framework import serializers
from .models import Stop, Route, RouteStop, Trip


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = [
            "id",
            "tenant",
            "provider",
            "external_id",
            "code",
            "name",
            "lat",
            "lng",
            "address",
            "zone",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "provider", "created_at", "updated_at"]


class RouteSerializer(serializers.ModelSerializer):
    stops_sequence = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = Route
        fields = [
            "id",
            "tenant",
            "provider",
            "external_id",
            "code",
            "name",
            "mode",
            "direction",
            "active",
            "stops_sequence",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "provider", "created_at", "updated_at"]

    def create(self, validated_data):
        stops_sequence = validated_data.pop("stops_sequence", [])
        route = super().create(validated_data)
        from .models import RouteStop, Stop

        for idx, stop_id in enumerate(stops_sequence):
            RouteStop.objects.create(
                route=route,
                stop=Stop.objects.get(id=stop_id, tenant=route.tenant, provider=route.provider),
                sequence_index=idx,
            )
        return route

    def update(self, instance, validated_data):
        stops_sequence = validated_data.pop("stops_sequence", None)
        route = super().update(instance, validated_data)
        from .models import RouteStop, Stop

        if stops_sequence is not None:
            RouteStop.objects.filter(route=route).delete()
            for idx, stop_id in enumerate(stops_sequence):
                RouteStop.objects.create(
                    route=route,
                    stop=Stop.objects.get(id=stop_id, tenant=route.tenant, provider=route.provider),
                    sequence_index=idx,
                )
        return route


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "id",
            "tenant",
            "provider",
            "route",
            "external_id",
            "service_date",
            "departure_time",
            "arrival_time",
            "vehicle_type",
            "vehicle_capacity",
            "operating_days",
            "time_zone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "provider",
            "created_at",
            "updated_at",
        ]
