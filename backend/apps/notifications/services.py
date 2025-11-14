import hashlib
import hmac
import json
from typing import Dict

import requests
from django.utils import timezone

from .models import WebhookEndpoint, NotificationEvent
from apps.tenancy.models import Tenant


def enqueue_event(tenant: Tenant, event_type: str, payload: Dict) -> NotificationEvent:
    """
    Create NotificationEvent and synchronously dispatch webhooks for now.
    You can later move dispatch into Celery workers.
    """
    event = NotificationEvent.objects.create(
        tenant=tenant,
        event_type=event_type,
        payload=payload,
        status="PENDING",
    )
    dispatch_event(event)
    return event

def dispatch_event(event: NotificationEvent):
    endpoints = WebhookEndpoint.objects.filter(
        tenant=event.tenant,
        is_active=True,
        event_types__contains=[event.event_type],
    )

    if not endpoints.exists():
        event.status = "SENT"  # nothing to do, but don't leave as pending
        event.save(update_fields=["status", "updated_at"])
        return

    payload_bytes = json.dumps(event.payload).encode("utf-8")

    last_error = ""
    success_any = False

    for ep in endpoints:
        signature = _sign_payload(ep.secret, payload_bytes)
        headers = {
            "Content-Type": "application/json",
            "X-GeoConnect-Event": event.event_type,
            "X-GeoConnect-Signature": signature,
        }
        try:
            resp = requests.post(ep.url, data=payload_bytes, headers=headers, timeout=5)
            if 200 <= resp.status_code < 300:
                success_any = True
            else:
                last_error = f"Endpoint {ep.url} returned {resp.status_code}"
        except Exception as exc:  # noqa
            last_error = str(exc)

    event.attempts += 1
    event.updated_at = timezone.now()
    if success_any:
        event.status = "SENT"
        event.last_error = ""
    else:
        event.status = "FAILED"
        event.last_error = last_error
    event.save(update_fields=["status", "attempts", "last_error", "updated_at"])


def _sign_payload(secret: str, payload: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
    return mac.hexdigest()
