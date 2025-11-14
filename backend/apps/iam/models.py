import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.tenancy.models import Tenant
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("PLATFORM_SUPER_ADMIN", "Platform Super Admin"),
        ("TENANT_OWNER", "Tenant Owner"),
        ("TENANT_ADMIN", "Tenant Admin"),
        ("TENANT_FINANCE_ADMIN", "Tenant Finance Admin"),
        ("TENANT_SUPPORT", "Tenant Support"),
        ("PROVIDER_MANAGER", "Provider Manager"),
        ("PROVIDER_STAFF", "Provider Staff"),
        ("PASSENGER", "Passenger"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, null=True, blank=True, related_name="users"
    )
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="PASSENGER")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "user"
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
