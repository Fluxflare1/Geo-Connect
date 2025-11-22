from django.urls import path

from .views import TripSearchView, TripSummaryView

urlpatterns = [
    path("search", TripSearchView.as_view(), name="trip-search"),
    path("<str:trip_id>/summary", TripSummaryView.as_view(), name="trip-summary"),
]
