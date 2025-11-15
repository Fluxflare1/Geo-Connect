import uuid
from django.db import models

from apps.tenancy.models import Tenant
from apps.providers.models import Provider


class SettlementBatch(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="settlement_batches")

    from_date = models.DateField()
    to_date = models.DateField()

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "settlement_batch"
        indexes = [
            models.Index(fields=["tenant", "from_date", "to_date"]),
        ]

    def __str__(self) -> str:
        return f"Settlement {self.id} ({self.from_date} -> {self.to_date})"


class SettlementItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(SettlementBatch, on_delete=models.CASCADE, related_name="items")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="settlement_items")

    bookings_count = models.PositiveIntegerField(default=0)
    booking_amount = models.BigIntegerField(default=0)
    paid_amount = models.BigIntegerField(default=0)
    commission_rate = models.FloatField(default=0.0)
    commission_amount = models.BigIntegerField(default=0)
    net_payout = models.BigIntegerField(default=0)

    currency = models.CharField(max_length=10, default="NGN")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "settlement_item"
        indexes = [
            models.Index(fields=["batch", "provider"]),
        ]

    def __str__(self) -> str:
        return f"SettlementItem {self.id} - {self.provider_id}"


