from rest_framework import serializers
from .models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = [
            "id",
            "tenant",
            "name",
            "legal_name",
            "modes",
            "regions",
            "status",
            "contact_email",
            "contact_phone",
            "supports_real_time",
            "supports_seat_selection",
            "branding",
            "integration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class ProviderPublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = [
            "id",
            "name",
            "legal_name",
            "modes",
            "regions",
            "supports_real_time",
            "supports_seat_selection",
            "branding",
            "integration",
        ]
