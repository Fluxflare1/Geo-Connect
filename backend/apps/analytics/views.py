from datetime import datetime, timedelta

from django.db.models import Count, Sum
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.iam.permissions import IsTenantAdmin
from apps.bookings.models import Booking
from apps.payments.models import PaymentTransaction
from apps.providers.models import Provider

class AdminOverviewDashboardView(generics.GenericAPIView):
    """
    GET /api/v1/admin/dashboard/overview?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD

    Default: last 30 days.
    """
    permission_classes = [IsAuthenticated, IsTenantAdmin]

    def get(self, request, *args, **kwargs):
        tenant = request.tenant

        to_date_str = request.query_params.get("to_date")
        from_date_str = request.query_params.get("from_date")

        if to_date_str:
            to_date = parse_date(to_date_str)
        else:
            to_date = datetime.utcnow().date()

        if from_date_str:
            from_date = parse_date(from_date_str)
        else:
            from_date = to_date - timedelta(days=30)

        bookings_qs = Booking.objects.filter(
            tenant=tenant,
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
        )

        payments_qs = PaymentTransaction.objects.filter(
            tenant=tenant,
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
            status="SUCCESS",
        )

        total_bookings = bookings_qs.count()
        bookings_by_status = (
            bookings_qs.values("status").annotate(count=Count("id")).order_by()
        )

        total_revenue = payments_qs.aggregate(total=Sum("amount"))["total"] or 0

        provider_stats = (
            bookings_qs.values("provider_id")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        provider_map = {
            p.id: p.name for p in Provider.objects.filter(tenant=tenant, id__in=[x["provider_id"] for x in provider_stats])
        }

        providers_list = [
            {
                "provider_id": str(row["provider_id"]),
                "provider_name": provider_map.get(row["provider_id"], ""),
                "bookings_count": row["count"],
            }
            for row in provider_stats
        ]

        return Response(
            {
                "range": {
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat(),
                },
                "bookings": {
                    "total": total_bookings,
                    "by_status": list(bookings_by_status),
                },
                "revenue": {
                    "total_amount": total_revenue,
                    "currency": "NGN",  # per-tenant later
                },
                "providers": providers_list,
            },
            status=status.HTTP_200_OK,
        )



class AdminSettlementSummaryView(generics.GenericAPIView):
    """
    GET /api/v1/admin/reports/settlements?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD

    Basic settlement preview aggregated from bookings & payments:
      - total booking value
      - total successful payments
      - estimated commission & net payout
    """
    permission_classes = [IsAuthenticated, IsTenantAdmin]

    def get(self, request, *args, **kwargs):
        tenant = request.tenant

        to_date_str = request.query_params.get("to_date")
        from_date_str = request.query_params.get("from_date")

        if to_date_str:
            to_date = parse_date(to_date_str)
        else:
            to_date = datetime.utcnow().date()

        if from_date_str:
            from_date = parse_date(from_date_str)
        else:
            from_date = to_date - timedelta(days=30)

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
                payments_count=Count("id"),
            )
            .order_by()
        )

        pay_map = {row["provider_id"]: row for row in payments_agg}
        provider_ids = list({row["provider_id"] for row in bookings_agg} | set(pay_map.keys()))
        providers = {
            p.id: p
            for p in Provider.objects.filter(tenant=tenant, id__in=provider_ids)
        }

        items = []
        for row in bookings_agg:
            provider_id = row["provider_id"]
            booking_amount = row["booking_amount"] or 0
            bookings_count = row["bookings_count"]
            payment_info = pay_map.get(provider_id, {})
            paid_amount = payment_info.get("paid_amount") or 0

            # simple default commission 10% – can be moved to provider config later
            commission_rate = 0.10
            commission_amount = int(booking_amount * commission_rate)
            net_payout = booking_amount - commission_amount

            provider = providers.get(provider_id)
            items.append(
                {
                    "provider_id": str(provider_id),
                    "provider_name": provider.name if provider else "",
                    "bookings_count": bookings_count,
                    "booking_amount": booking_amount,
                    "paid_amount": paid_amount,
                    "commission_rate": commission_rate,
                    "commission_amount": commission_amount,
                    "net_payout": net_payout,
                }
            )

        return Response(
            {
                "range": {
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat(),
                },
                "items": items,
                "currency": "NGN",
            },
            status=status.HTTP_200_OK,
        )


