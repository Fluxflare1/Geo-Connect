import uuid
from django.db import models

from apps.tenancy.models import Tenant
from apps.iam.models import User
from apps.bookings.models import Booking
from apps.providers.models import Provider


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    CATEGORY_CHOICES = [
        ("BOOKING", "Booking"),
        ("PAYMENT", "Payment"),
        ("TRIP", "Trip"),
        ("ACCOUNT", "Account"),
        ("OTHER", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="support_tickets")

    customer_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_tickets"
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_support_tickets"
    )

    provider = models.ForeignKey(
        Provider, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_tickets"
    )
    booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_tickets"
    )

    subject = models.CharField(max_length=255)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default="OTHER")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="OPEN")
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="MEDIUM")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "support_ticket"
        indexes = [
            models.Index(fields=["tenant", "status", "priority"]),
            models.Index(fields=["tenant", "customer_user"]),
        ]

    def __str__(self) -> str:
        return f"{self.id} - {self.subject}"


class SupportMessage(models.Model):
    SENDER_TYPE_CHOICES = [
        ("CUSTOMER", "Customer"),
        ("AGENT", "Agent"),
        ("SYSTEM", "System"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_messages"
    )
    sender_type = models.CharField(max_length=16, choices=SENDER_TYPE_CHOICES)

    body = models.TextField()
    internal_only = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "support_message"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Message {self.id} on ticket {self.ticket_id}"
