import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

from apps.tenancy.models import Tenant


class WebhookEndpoint(models.Model):
    """
    Tenant-level webhook endpoint for events like booking.created, booking.cancelled, ticket.issued
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="webhook_endpoints")

    name = models.CharField(max_length=255)
    url = models.URLField()
    secret = models.CharField(max_length=255, help_text="Signing secret for HMAC")

    event_types = ArrayField(models.CharField(max_length=64), default=list, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "webhook_endpoint"
        indexes = [
            models.Index(fields=["tenant"]),
        ]

    def __str__(self) -> str:
        return f"{self.tenant.slug} - {self.name}"


class NotificationEvent(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="notification_events")

    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING")
    attempts = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_event"
        indexes = [
            models.Index(fields=["tenant", "event_type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.tenant.slug})"


