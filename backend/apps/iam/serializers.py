from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "tenant",
            "email",
            "role",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "tenant", "is_active", "date_joined"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    device = serializers.DictField(required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.", code="authorization")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.", code="authorization")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }


class MeSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "tenant",
            "email",
            "role",
            "permissions",
            "profile",
        ]

    def get_permissions(self, obj):
        # Simple mapping for now; you can expand later.
        perms = []
        if obj.role in ["PASSENGER"]:
            perms.extend(["booking:create", "booking:view:self"])
        if obj.role in ["TENANT_ADMIN", "TENANT_OWNER", "PLATFORM_SUPER_ADMIN"]:
            perms.extend(["admin:tenants:view", "admin:users:manage"])
        return perms

    def get_profile(self, obj):
        return {
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "phone": None,
            "preferred_language": "en",
            "country": None,
            "time_zone": "Africa/Lagos",
        }
