import uuid
from typing import Dict

from django.urls import reverse

from .models import PaymentTransaction
from apps.bookings.models import Booking


def create_payment_for_booking(request, booking: Booking, provider_code: str) -> Dict:
    """
    Create PaymentTransaction for a booking.

    NOTE:
      - This does NOT call an external PSP yet.
      - In a real implementation you will:
          * Call the PSP API with amount/currency/reference
          * Receive a real redirect_url
          * Store PSP response in raw_payload
    """
    reference = f"{provider_code}_bk_{booking.id.hex[:12]}_{uuid.uuid4().hex[:6]}".upper()

    payment = PaymentTransaction.objects.create(
        tenant=booking.tenant,
        provider=booking.provider,
        booking=booking,
        psp=provider_code,
        psp_reference=reference,
        amount=booking.total_amount,
        currency=booking.currency,
        status="INITIATED",
        metadata={"booking_id": str(booking.id)},
    )

    webhook_path = reverse("payments-webhook", kwargs={"provider": provider_code})
    callback_url = request.build_absolute_uri(webhook_path)

    # redirect_url will be overwritten once PSP integration is wired;
    # for now we provide a structured placeholder.
    redirect_url = f"https://{provider_code}.example/checkout/{reference}"

    return {
        "provider": provider_code,
        "payment_reference": payment.psp_reference,
        "redirect_url": redirect_url,
        "callback_url": callback_url,
        "status": payment.status,
    }
