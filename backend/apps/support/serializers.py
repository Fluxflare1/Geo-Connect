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
