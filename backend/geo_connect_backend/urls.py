from django.contrib import admin
from django.urls import path, include
from apps.iam.views import LoginView, MeView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health / readiness (used by Nginx / load balancers / k8s probes)
    path("api/v1/", include("apps.observability.urls")),

    # Auth
    path("api/v1/auth/login", LoginView.as_view(), name="auth-login"),
    path("api/v1/auth/refresh", TokenRefreshView.as_view(), name="auth-refresh"),
    path("api/v1/auth/me", MeView.as_view(), name="auth-me"),

    # Admin APIs
    path("api/v1/admin/", include("apps.admin_api.urls")),
    path("api/v1/admin/", include("apps.notifications.urls")),
    path("api/v1/admin/", include("apps.analytics.urls")),
    path("api/v1/admin/", include("apps.settlement.urls")),
    path("api/v1/admin/", include("apps.support.urls")),

    # Provider profile
    path("api/v1/provider/", include("apps.providers.urls")),

    # Provider bulk + catalog + realtime
    path("api/v1/provider/", include("apps.catalog.urls")),
    path("api/v1/provider/", include("apps.realtime.urls")),

    # Public/catalog + flows
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/", include("apps.trips.urls")),
    path("api/v1/", include("apps.bookings.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.support.urls")),

    path("api/v1/auth/", include("apps.iam.urls")),
]
