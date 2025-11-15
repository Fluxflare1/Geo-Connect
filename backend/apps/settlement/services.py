from datetime import datetime
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone

from apps.bookings.models import Booking
from apps.payments.models import PaymentTransaction
from apps.providers.models import Provider
from apps.tenancy.models import Tenant
from .models import SettlementBatch, SettlementItem


@transaction.atomic
def generate_settlement_batch(tenant: Tenant, from_date, to_date) -> SettlementBatch:
    """
    Creates a SettlementBatch and SettlementItems per provider, based on:
      - CONFIRMED bookings in range
      - SUCCESS payments in range
      - Flat 10% commission (can be moved to provider config)
    """
    batch = SettlementBatch.objects.create(
        tenant=tenant,
        from_date=from_date,
        to_date=to_date,
        status="PENDING",
    )

    bookings_qs = Booking.objects.filter(
        tenant=tenant,
        status="CONFIRMED",
        created_at__date__gte=from_date,
        created_at__date__lte=to_date,
    )

    payments_qs = PaymentTransaction.objects.filter(
        tenant=tenant,
        status="SUCCESS",
        created_at__date__gte=from_date,
        created_at__date__lte=to_date,
    )

    bookings_agg = (
        bookings_qs.values("provider_id")
        .annotate(
            booking_amount=Sum("total_amount"),
            bookings_count=Count("id"),
        )
        .order_by()
    )

    payments_agg = (
        payments_qs.values("provider_id")
        .annotate(
            paid_amount=Sum("amount"),
        )
        .order_by()
    )

    pay_map = {row["provider_id"]: row for row in payments_agg}
    provider_ids = list({row["provider_id"] for row in bookings_agg} | set(pay_map.keys()))
    providers = {
        p.id: p for p in Provider.objects.filter(tenant=tenant, id__in=provider_ids)
    }

    for row in bookings_agg:
        provider_id = row["provider_id"]
        booking_amount = row["booking_amount"] or 0
        bookings_count = row["bookings_count"]

        payment_info = pay_map.get(provider_id, {})
        paid_amount = payment_info.get("paid_amount") or 0

        # TODO: read commission from Provider.config if present
        commission_rate = 0.10
        commission_amount = int(booking_amount * commission_rate)
        net_payout = booking_amount - commission_amount

        provider = providers.get(provider_id)
        SettlementItem.objects.create(
            batch=batch,
            provider=provider,
            bookings_count=bookings_count,
            booking_amount=booking_amount,
            paid_amount=paid_amount,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            net_payout=net_payout,
            currency="NGN",
        )

    batch.status = "COMPLETED"
    batch.completed_at = timezone.now()
    batch.save(update_fields=["status", "completed_at"])
    return batch


