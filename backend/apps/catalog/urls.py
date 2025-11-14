from django.urls import path

from .views import (
    ProviderStopsBulkUpsertView,
    ProviderRoutesBulkUpsertView,
    ProviderTripsBulkUpsertView,
    StopListView,
    RouteListView,
    TripListView,
)

urlpatterns = [
    # Provider integration bulk endpoints (mounted under /api/v1/provider/)
    path("stops", ProviderStopsBulkUpsertView.as_view(), name="provider-stops-bulk"),
    path("routes", ProviderRoutesBulkUpsertView.as_view(), name="provider-routes-bulk"),
    path("trips", ProviderTripsBulkUpsertView.as_view(), name="provider-trips-bulk"),

    # Catalog read endpoints (mounted under /api/v1/catalog/)
    path("catalog/stops", StopListView.as_view(), name="catalog-stops-list"),
    path("catalog/routes", RouteListView.as_view(), name="catalog-routes-list"),
    path("catalog/trips", TripListView.as_view(), name="catalog-trips-list"),
]
