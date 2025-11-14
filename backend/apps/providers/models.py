import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

from apps.tenancy.models import Tenant


class Provider(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("SUSPENDED", "Suspended"),
        ("TERMINATED", "Terminated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="providers")

    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    modes = ArrayField(models.CharField(max_length=20), default=list, blank=True)
    regions = ArrayField(models.CharField(max_length=32), default=list, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)

    supports_real_time = models.BooleanField(default=False)
    supports_seat_selection = models.BooleanField(default=False)

    branding = models.JSONField(default=dict, blank=True)
    integration = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "provider"
        ordering = ["name"]
        unique_together = ("tenant", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.tenant.slug})"
