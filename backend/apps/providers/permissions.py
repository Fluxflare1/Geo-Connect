from rest_framework.permissions import BasePermission
from apps.iam.models import User
from .models import Provider


class IsProviderUserOrTenantAdmin(BasePermission):
    """
    Used for /api/v1/provider/* endpoints.

    Requires:
    - Authenticated user
    - X-Tenant-ID resolved to tenant
    - X-Provider-ID header that belongs to that tenant
    - User is either:
        - Provider Manager / Provider Staff for that tenant, or
        - Tenant admin / owner, or
        - Platform super admin
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        tenant = getattr(request, "tenant", None)
        provider_id = request.headers.get("X-Provider-ID")
        if not provider_id:
            return False

        try:
            provider = Provider.objects.get(id=provider_id, tenant=tenant)
        except Provider.DoesNotExist:
            return False

        request.provider = provider  # attach for later use

        # Platform super admin can access any.
        if user.role == "PLATFORM_SUPER_ADMIN":
            return True

        # Tenant admin/owner can manage providers in their tenant.
        if user.role in ["TENANT_OWNER", "TENANT_ADMIN"] and user.tenant_id == provider.tenant_id:
            return True

        # Provider-specific roles must be within same tenant.
        if user.role in ["PROVIDER_MANAGER", "PROVIDER_STAFF"] and user.tenant_id == provider.tenant_id:
            return True

        return False
