import uuid
from django.db import models


class Tenant(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("SUSPENDED", "Suspended"),
        ("TERMINATED", "Terminated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    primary_domain = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    region = models.CharField(max_length=10, blank=True)
    default_currency = models.CharField(max_length=10, default="NGN")
    
    region_code = models.CharField(
        max_length=16,
        default="africa-west-1",
        help_text="Logical region for this tenant (e.g. africa-west-1, eu-central-1).",
    )

    branding = models.JSONField(default=dict, blank=True)
    config = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenant"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"
