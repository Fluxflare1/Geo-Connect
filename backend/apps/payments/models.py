import uuid
from django.db import models

from apps.tenancy.models import Tenant
from apps.providers.models import Provider
from apps.bookings.models import Booking


class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("INITIATED", "Initiated"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="payments")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="payments", null=True, blank=True
    )
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")

    psp = models.CharField(max_length=50)  # e.g. 'paystack', 'flutterwave'
    psp_reference = models.CharField(max_length=255, unique=True)

    amount = models.BigIntegerField()
    currency = models.CharField(max_length=10, default="NGN")

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="INITIATED")

    raw_payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_transaction"
        indexes = [
            models.Index(fields=["tenant", "booking"]),
            models.Index(fields=["psp", "psp_reference"]),
        ]

    def __str__(self) -> str:
        return f"{self.psp} {self.psp_reference} ({self.status})"
