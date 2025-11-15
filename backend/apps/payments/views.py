from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentTransaction
from .services import mark_payment_success, mark_payment_failed
from apps.bookings.services import confirm_booking_and_issue_tickets
from apps.core.services import register_idempotency_key, IdempotencyError


class PaymentWebhookView(APIView):
    """
    POST /api/v1/payments/webhooks/{provider}

    This view expects PSP-specific payloads. For now, we handle a generic structure:
      {
        "event": "...",
        "data": {
          "reference": "...",
          "amount": ...,
          "currency": "NGN",
          "status": "success" | "failed",
          "metadata": {
            "booking_id": "...",
            "tenant_id": "..."
          }
        }
      }

    In production, you'll:
      - Verify signature from headers
      - Map actual PSP fields into this structure at the integration layer
    """

    permission_classes = [AllowAny]

    def post(self, request, provider: str, *args, **kwargs):
        payload = request.data

        event = payload.get("event")
        data = payload.get("data") or {}
        reference = data.get("reference")
        status_str = (data.get("status") or "").lower()

        if not reference:
            return Response(
                {
                    "error": {
                        "code": "MISSING_REFERENCE",
                        "message": "Payment reference is required.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = PaymentTransaction.objects.select_related("booking", "tenant").get(
                psp_reference=reference
            )
        except PaymentTransaction.DoesNotExist:
            return Response(
                {
                    "error": {
                        "code": "PAYMENT_NOT_FOUND",
                        "message": "Payment transaction not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # TODO: verify signature using PSP secret (implement per-provider).

        if status_str in ["success", "successful"]:
            payment = mark_payment_success(payment, payload)
            booking = payment.booking
            confirm_booking_and_issue_tickets(booking)
            response_body = {
                "received": True,
                "booking_id": str(booking.id),
                "status": booking.status,
            }
            return Response(response_body, status=status.HTTP_200_OK)

        elif status_str in ["failed", "error"]:
            payment = mark_payment_failed(payment, payload)
            booking = payment.booking
            if booking.status == "PENDING_PAYMENT":
                booking.status = "PAYMENT_FAILED"
                booking.save(update_fields=["status", "updated_at"])
            response_body = {
                "received": True,
                "booking_id": str(booking.id),
                "status": booking.status,
            }
            return Response(response_body, status=status.HTTP_200_OK)

        else:
            # Unknown or unhandled status – acknowledge to avoid PSP retries storm
            return Response({"received": True}, status=status.HTTP_200_OK)
