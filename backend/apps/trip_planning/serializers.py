from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.catalog.models import TravelMode


class LocationInputSerializer(serializers.Serializer):
    TYPE_STOP_ID = "STOP_ID"
    TYPE_CITY_CODE = "CITY_CODE"
    TYPE_COORDINATES = "COORDINATES"

    type = serializers.ChoiceField(
        choices=[TYPE_STOP_ID, TYPE_CITY_CODE, TYPE_COORDINATES]
    )
    value = serializers.CharField(max_length=128)


class TripSearchFiltersSerializer(serializers.Serializer):
    providers = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        default=list,
    )
    max_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True
    )
    direct_only = serializers.BooleanField(required=False, default=False)


class TripSearchRequestSerializer(serializers.Serializer):
    origin = LocationInputSerializer()
    destination = LocationInputSerializer()
    departure_date = serializers.DateField()
    departure_time = serializers.CharField(
        required=False, allow_blank=True, default="ANY"
    )
    passengers = serializers.IntegerField(min_value=1, default=1)
    mode = serializers.ChoiceField(
        choices=["ANY"] + [choice[0] for choice in TravelMode.choices],
        default="ANY",
    )
    filters = TripSearchFiltersSerializer(required=False)
    sort_by = serializers.ChoiceField(
        choices=["DEPARTURE_TIME", "PRICE", "ARRIVAL_TIME", "DURATION"],
        default="DEPARTURE_TIME",
    )
    sort_order = serializers.ChoiceField(
        choices=["ASC", "DESC"],
        default="ASC",
    )

    def validate_departure_date(self, value):
        # Enforce today/future (you can relax this for history if needed)
        if value < timezone.localdate():
            raise serializers.ValidationError("departure_date cannot be in the past.")
        return value


class TripPriceSerializer(serializers.Serializer):
    currency = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    per_passenger = serializers.DecimalField(max_digits=12, decimal_places=2)
    fees_included = serializers.BooleanField()


class TripProviderSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    logo_url = serializers.CharField(allow_blank=True)


class TripStopSerializer(serializers.Serializer):
    stop_id = serializers.CharField()
    name = serializers.CharField()
    city_code = serializers.CharField(allow_blank=True)


class TripResultSerializer(serializers.Serializer):
    trip_id = serializers.CharField()
    provider = TripProviderSerializer()
    mode = serializers.CharField()
    product_type = serializers.CharField()
    origin = TripStopSerializer()
    destination = TripStopSerializer()
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField()
    available_seats = serializers.IntegerField()
    price = TripPriceSerializer()
    constraints = serializers.DictField(child=serializers.BooleanField(), default=dict)
    tags = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    preview = serializers.DictField(child=serializers.CharField(), default=dict)


class TripSearchResponseSerializer(serializers.Serializer):
    search_id = serializers.UUIDField()
    currency = serializers.CharField()
    results = TripResultSerializer(many=True)


class TripSummarySerializer(serializers.Serializer):
    trip_id = serializers.CharField()
    provider = TripProviderSerializer()
    mode = serializers.CharField()
    product_type = serializers.CharField()
    origin = TripStopSerializer()
    destination = TripStopSerializer()
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField()
    available_seats = serializers.IntegerField()
    currency = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    per_passenger_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    fare_rules = serializers.DictField()
