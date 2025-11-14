from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Resolve tenant from:
      - X-Tenant-ID header, or
      - subdomain (e.g. tenant.slug.geo-connect.com)

    Public endpoints (like /auth/login) can work with or without tenant,
    but **admin & business APIs** will require tenant explicitly.
    """

    def process_request(self, request):
        request.tenant = None

        header_tenant_id = request.headers.get("X-Tenant-ID")
        host = request.get_host().split(":")[0]  # remove port
        subdomain = None

        # Very basic subdomain parsing: slug.geo-connect.com
        parts = host.split(".")
        if len(parts) > 2:
            subdomain = parts[0]

        tenant = None

        if header_tenant_id:
            try:
                tenant = Tenant.objects.get(id=header_tenant_id, status__in=["PENDING", "ACTIVE"])
            except Tenant.DoesNotExist:
                return JsonResponse(
                    {"error": {"code": "TENANT_NOT_FOUND", "message": "Invalid X-Tenant-ID"}},
                    status=400,
                )

        elif subdomain and subdomain not in ["www", "api"]:
            try:
                tenant = Tenant.objects.get(slug=subdomain, status__in=["PENDING", "ACTIVE"])
            except Tenant.DoesNotExist:
                tenant = None

        request.tenant = tenant

        # For admin-level platform-wide endpoints, we allow tenant to be None.
        # For others, views can enforce tenant requirement via permissions.
        return None
