from datetime import timedelta
from django.utils import timezone
from django.db import IntegrityError

from .models import IdempotencyKey


class IdempotencyError(Exception):
    pass


def register_idempotency_key(key: str, endpoint_slug: str, ttl_seconds: int = 600):
    """
    Tries to register a (key, endpoint_slug) pair.
    Raises IdempotencyError if already used.
    """
    expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
    try:
        IdempotencyKey.objects.create(
            key=key,
            endpoint_slug=endpoint_slug,
            expires_at=expires_at,
        )
    except IntegrityError:
        raise IdempotencyError(f"Idempotency key already used for {endpoint_slug}")
