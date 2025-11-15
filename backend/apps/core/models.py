import uuid
from django.db import models
from django.utils import timezone


class IdempotencyKey(models.Model):
    """
    Generic idempotency key for POST operations (bookings, webhooks, etc).

    Scope is (key, endpoint_slug).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key = models.CharField(max_length=255)
    endpoint_slug = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "idempotency_key"
        unique_together = ("key", "endpoint_slug")

    def __str__(self) -> str:
        return f"{self.endpoint_slug}:{self.key}"
