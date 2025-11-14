from django.urls import path

from .views import (
    ProviderVehicleLocationsView,
    ProviderTripStatusView,
    ProviderTripInventoryView,
    ProviderServiceAlertsView,
)

urlpatterns = [
    path(
        "vehicles/locations",
        ProviderVehicleLocationsView.as_view(),
        name="provider-vehicles-locations",
    ),
    path(
        "trips/status",
        ProviderTripStatusView.as_view(),
        name="provider-trips-status",
    ),
    path(
        "trips/inventory",
        ProviderTripInventoryView.as_view(),
        name="provider-trips-inventory",
    ),
    path(
        "service-alerts",
        ProviderServiceAlertsView.as_view(),
        name="provider-service-alerts",
    ),
]
