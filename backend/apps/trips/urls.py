from django.urls import path
from .views import TripSearchView

urlpatterns = [
    path("trips/search", TripSearchView.as_view(), name="trips-search"),
]
