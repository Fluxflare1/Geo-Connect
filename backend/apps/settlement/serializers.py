from rest_framework import serializers
from .models import SettlementBatch, SettlementItem


class SettlementItemSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.name", read_only=True)

    class Meta:
        model = SettlementItem
        fields = [
            "id",
            "provider_id",
            "provider_name",
            "bookings_count",
            "booking_amount",
            "paid_amount",
            "commission_rate",
            "commission_amount",
            "net_payout",
            "currency",
            "created_at",
        ]
        read_only_fields = fields


class SettlementBatchSerializer(serializers.ModelSerializer):
    items = SettlementItemSerializer(many=True, read_only=True)

    class Meta:
        model = SettlementBatch
        fields = [
            "id",
            "from_date",
            "to_date",
            "status",
            "notes",
            "created_at",
            "completed_at",
            "items",
        ]
        read_only_fields = ["id", "status", "created_at", "completed_at", "items"]

  class SettlementBatchCreateSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True)


