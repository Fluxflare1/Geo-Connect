from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPlatformSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == "PLATFORM_SUPER_ADMIN"
        )


class IsTenantAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.role in ["TENANT_OWNER", "TENANT_ADMIN", "PLATFORM_SUPER_ADMIN"]


class IsTenantAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsTenantAdmin().has_permission(request, view)
