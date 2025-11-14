from django.urls import path
from .views import BookingCreateView, BookingDetailView, BookingCancelView

urlpatterns = [
    path("bookings", BookingCreateView.as_view(), name="bookings-create"),
    path("bookings/<uuid:booking_id>", BookingDetailView.as_view(), name="bookings-detail"),
    path("bookings/<uuid:booking_id>/cancel", BookingCancelView.as_view(), name="bookings-cancel"),
]
