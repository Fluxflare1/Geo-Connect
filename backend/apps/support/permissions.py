from rest_framework.permissions import BasePermission


class IsTenantSupportOrAdmin(BasePermission):
    """
    TENANT_SUPPORT, TENANT_ADMIN, TENANT_OWNER, PLATFORM_SUPER_ADMIN
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.role in [
            "TENANT_SUPPORT",
            "TENANT_ADMIN",
            "TENANT_OWNER",
            "PLATFORM_SUPER_ADMIN",
        ]
