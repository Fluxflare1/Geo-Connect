from rest_framework import serializers

from .models import Booking, BookingPassenger, BookingSeat, Ticket
from apps.catalog.models import Trip
from apps.providers.models import Provider


class BookingPassengerInputSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["ADULT", "CHILD", "SENIOR"])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)


class SeatSelectionSerializer(serializers.Serializer):
    enabled = serializers.BooleanField(default=False)
    requested_seats = serializers.ListField(
        child=serializers.CharField(max_length=16), required=False
    )


class PaymentInputSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=50)
    currency = serializers.CharField(max_length=10)
    amount = serializers.IntegerField()  # client-sent; we will override with server price


class BookingCreateSerializer(serializers.Serializer):
    trip_id = serializers.UUIDField()
    passengers = BookingPassengerInputSerializer(many=True)
    seat_selection = SeatSelectionSerializer(required=False)
    payment = PaymentInputSerializer()
    customer_context = serializers.DictField(required=False)

    def validate(self, attrs):
        if not attrs["passengers"]:
            raise serializers.ValidationError("At least one passenger is required.")
        return attrs



class BookingPassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingPassenger
        fields = [
            "id",
            "passenger_type",
            "first_name",
            "last_name",
            "email",
            "phone",
        ]



class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_code",
            "qr_payload",
            "status",
            "valid_from",
            "valid_until",
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    passengers = BookingPassengerSerializer(many=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "tenant",
            "provider",
            "trip",
            "customer_user",
            "status",
            "reservation_expires_at",
            "total_amount",
            "currency",
            "seats_count",
            "metadata",
            "passengers",
            "tickets",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class BookingCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)
