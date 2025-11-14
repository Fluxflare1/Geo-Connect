import uuid
from django.db import models
from apps.tenancy.models import Tenant
from apps.providers.models import Provider


class PricingRule(models.Model):
    TYPE_CHOICES = [
        ("DISTANCE_BASED", "Distance-based base fare"),
        ("TIME_BASED", "Time-based base fare"),
        ("FIXED", "Fixed fare"),
        ("SURCHARGE", "Surcharge"),
        ("DISCOUNT", "Discount"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="pricing_rules")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="pricing_rules", null=True, blank=True
    )

    name = models.CharField(max_length=255)
    mode = models.CharField(max_length=20, blank=True)  # BUS, TRAIN, etc (optional filter)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=10, default="NGN")

    config = models.JSONField(default=dict, blank=True)
    conditions = models.JSONField(default=dict, blank=True)

    priority = models.IntegerField(default=100)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pricing_rule"
        ordering = ["priority", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"
