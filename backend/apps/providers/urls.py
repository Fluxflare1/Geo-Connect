from django.urls import path
from .views import ProviderProfileView

urlpatterns = [
    path("profile", ProviderProfileView.as_view(), name="provider-profile"),
]
