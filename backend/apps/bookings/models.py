import uuid
from django.db import models
from django.utils import timezone

from apps.tenancy.models import Tenant
from apps.providers.models import Provider
from apps.catalog.models import Trip
from apps.iam.models import User


class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING_PAYMENT", "Pending payment"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("PAYMENT_FAILED", "Payment failed"),
        ("EXPIRED", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="bookings")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="bookings")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="bookings")

    customer_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="PENDING_PAYMENT")
    reservation_expires_at = models.DateTimeField(null=True, blank=True)

    total_amount = models.BigIntegerField(default=0)  # minor units
    currency = models.CharField(max_length=10, default="NGN")

    seats_count = models.PositiveIntegerField(default=0)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "booking"
        indexes = [
            models.Index(fields=["tenant", "provider", "trip"]),
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self) -> str:
        return f"Booking {self.id} ({self.status})"

    @property
    def is_active(self) -> bool:
        if self.status not in ["PENDING_PAYMENT", "CONFIRMED"]:
            return False
        if self.status == "PENDING_PAYMENT" and self.reservation_expires_at:
            return self.reservation_expires_at > timezone.now()
        return True


class BookingPassenger(models.Model):
    PASSENGER_TYPES = [
        ("ADULT", "Adult"),
        ("CHILD", "Child"),
        ("SENIOR", "Senior"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="passengers")

    passenger_type = models.CharField(max_length=16, choices=PASSENGER_TYPES, default="ADULT")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "booking_passenger"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.passenger_type})"



class BookingSeat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="seats")
    passenger = models.ForeignKey(
        BookingPassenger, on_delete=models.CASCADE, related_name="seats"
    )
    seat_number = models.CharField(max_length=16, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "booking_seat"
        indexes = [
            models.Index(fields=["booking", "seat_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.booking_id} - {self.seat_number}"



class Ticket(models.Model):
    STATUS_CHOICES = [
        ("ISSUED", "Issued"),
        ("CANCELLED", "Cancelled"),
        ("USED", "Used"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="tickets")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="tickets")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="tickets")
    passenger = models.ForeignKey(
        BookingPassenger, on_delete=models.CASCADE, related_name="tickets"
    )

    ticket_code = models.CharField(max_length=64, unique=True)
    qr_payload = models.CharField(max_length=512, blank=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="ISSUED")
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticket"
        indexes = [
            models.Index(fields=["tenant", "provider"]),
            models.Index(fields=["booking"]),
        ]

    def __str__(self) -> str:
        return f"Ticket {self.ticket_code} ({self.status})"

