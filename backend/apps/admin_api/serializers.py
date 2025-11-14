from rest_framework import serializers
from apps.tenancy.models import Tenant
from apps.tenancy.serializers import TenantSerializer
from apps.iam.models import User
from apps.iam.serializers import UserProfileSerializer
from apps.providers.models import Provider


class TenantCreateSerializer(TenantSerializer):
    owner = serializers.DictField(write_only=True, required=False)

    class Meta(TenantSerializer.Meta):
        fields = TenantSerializer.Meta.fields + ["owner"]


class UserAdminSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        read_only_fields = ["id", "tenant", "date_joined"]


class ProviderAdminSerializer(serializers.ModelSerializer):
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
