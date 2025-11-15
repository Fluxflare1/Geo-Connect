from rest_framework import serializers
from .models import SupportTicket, SupportMessage


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = [
            "id",
            "sender_type",
            "sender_name",
            "body",
            "internal_only",
            "created_at",
        ]
        read_only_fields = fields

    def get_sender_name(self, obj):
        if obj.sender:
            name = (obj.sender.first_name or "") + " " + (obj.sender.last_name or "")
            return name.strip() or obj.sender.email
        return obj.sender_type



class SupportTicketCreateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    category = serializers.ChoiceField(
        choices=["BOOKING", "PAYMENT", "TRIP", "ACCOUNT", "OTHER"],
        default="OTHER",
    )
    priority = serializers.ChoiceField(
        choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], default="MEDIUM"
    )
    booking_id = serializers.UUIDField(required=False)
    provider_id = serializers.UUIDField(required=False)
    message = serializers.CharField()


class SupportTicketListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "subject",
            "category",
            "status",
            "priority",
            "booking_id",
            "provider_id",
            "created_at",
            "updated_at",
            "last_activity_at",
            "last_message",
        ]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        return {
            "sender_type": msg.sender_type,
            "body": msg.body[:120],
            "created_at": msg.created_at,
        }


class SupportTicketDetailSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "subject",
            "category",
            "status",
            "priority",
            "booking_id",
            "provider_id",
            "customer_user_id",
            "assigned_to_id",
            "created_at",
            "updated_at",
            "last_activity_at",
            "messages",
        ]
        read_only_fields = fields


class SupportTicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ["status", "priority", "assigned_to"]


class SupportMessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField()
    internal_only = serializers.BooleanField(default=False)



