from django.urls import path
from .views import (
    TenantListCreateView,
    TenantDetailView,
    TenantStatusUpdateView,
    TenantUserListCreateView,
    TenantUserDetailView,
)

urlpatterns = [
    # Tenants (platform-level)
    path("tenants", TenantListCreateView.as_view(), name="admin-tenants-list-create"),
    path("tenants/<uuid:tenant_id>", TenantDetailView.as_view(), name="admin-tenants-detail"),
    path("tenants/<uuid:tenant_id>/status", TenantStatusUpdateView.as_view(), name="admin-tenants-status"),

    # Users within a tenant (tenant admin)
    path("users", TenantUserListCreateView.as_view(), name="admin-users-list-create"),
    path("users/<uuid:user_id>", TenantUserDetailView.as_view(), name="admin-users-detail"),
]
