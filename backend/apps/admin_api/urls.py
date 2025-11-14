from django.urls import path
from .views import (
    TenantListCreateView,
    TenantDetailView,
    TenantStatusUpdateView,
    TenantUserListCreateView,
    TenantUserDetailView,
    ProviderListCreateView,
    ProviderDetailView,
    PricingRuleListCreateView,
    PricingRuleDetailView,
)

urlpatterns = [
    # Tenants
    path("tenants", TenantListCreateView.as_view(), name="admin-tenants-list-create"),
    path("tenants/<uuid:tenant_id>", TenantDetailView.as_view(), name="admin-tenants-detail"),
    path("tenants/<uuid:tenant_id>/status", TenantStatusUpdateView.as_view(), name="admin-tenants-status"),

    # Users
    path("users", TenantUserListCreateView.as_view(), name="admin-users-list-create"),
    path("users/<uuid:user_id>", TenantUserDetailView.as_view(), name="admin-users-detail"),

    # Providers
    path("providers", ProviderListCreateView.as_view(), name="admin-providers-list-create"),
    path("providers/<uuid:provider_id>", ProviderDetailView.as_view(), name="admin-providers-detail"),

    # Pricing rules
    path("pricing/rules", PricingRuleListCreateView.as_view(), name="admin-pricing-rules-list-create"),
    path("pricing/rules/<uuid:rule_id>", PricingRuleDetailView.as_view(), name="admin-pricing-rules-detail"),
]
