from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.tenancy.models import Tenant
from apps.iam.models import User
from apps.iam.permissions import IsPlatformSuperAdmin, IsTenantAdmin
from .serializers import TenantCreateSerializer, TenantSerializer, UserAdminSerializer


class TenantListCreateView(generics.ListCreateAPIView):
    """
    Platform super admin: list/create tenants.
    """
    permission_classes = [IsAuthenticated, IsPlatformSuperAdmin]
    serializer_class = TenantCreateSerializer
    queryset = Tenant.objects.all().order_by("name")

    @transaction.atomic
    def perform_create(self, serializer):
        tenant = serializer.save()
        owner_data = serializer.validated_data.get("owner")
        if owner_data:
            User.objects.create_user(
                email=owner_data["email"],
                password=None,  # you can send activation email flow later
                first_name=owner_data.get("first_name", ""),
                last_name=owner_data.get("last_name", ""),
                tenant=tenant,
                role="TENANT_OWNER",
                is_active=True,
            )
        return tenant


class TenantDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsPlatformSuperAdmin]
    serializer_class = TenantSerializer
    lookup_url_kwarg = "tenant_id"
    queryset = Tenant.objects.all()


class TenantStatusUpdateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsPlatformSuperAdmin]
    lookup_url_kwarg = "tenant_id"
    serializer_class = TenantSerializer

    def post(self, request, *args, **kwargs):
        tenant = Tenant.objects.get(id=kwargs[self.lookup_url_kwarg])
        previous_status = tenant.status
        new_status = request.data.get("status")
        reason = request.data.get("reason", "")

        if new_status not in dict(Tenant.STATUS_CHOICES):
            return Response(
                {"error": {"code": "INVALID_STATUS", "message": "Invalid tenant status."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tenant.status = new_status
        tenant.save(update_fields=["status", "updated_at"])

        # You can hook audit logging here (reason, notes).
        return Response(
            {
                "tenant_id": str(tenant.id),
                "previous_status": previous_status,
                "new_status": new_status,
                "reason": reason,
            },
            status=status.HTTP_200_OK,
        )


class TenantUserListCreateView(generics.ListCreateAPIView):
    """
    Tenant admin: manage users within their tenant.
    """
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = UserAdminSerializer

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.tenant).order_by("email")

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class TenantUserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = UserAdminSerializer
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.tenant)
