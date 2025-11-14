from rest_framework import serializers
from apps.tenancy.models import Tenant
from apps.tenancy.serializers import TenantSerializer
from apps.iam.models import User
from apps.iam.serializers import UserProfileSerializer


class TenantCreateSerializer(TenantSerializer):
    owner = serializers.DictField(write_only=True, required=False)

    class Meta(TenantSerializer.Meta):
        fields = TenantSerializer.Meta.fields + ["owner"]


class UserAdminSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        read_only_fields = ["id", "tenant", "date_joined"]
