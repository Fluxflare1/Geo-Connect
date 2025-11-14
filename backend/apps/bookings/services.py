import uuid
from datetime import timedelta
from typing import List, Dict

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.catalog.models import Trip, RouteStop
from apps.pricing.services import calculate_fare_for_trip_from_route
from apps.tenancy.models import Tenant
from apps.providers.models import Provider
from apps.iam.models import User
from .models import Booking, BookingPassenger, BookingSeat, Ticket
from apps.notifications.services import enqueue_event


@transaction.atomic
def create_booking(
    tenant: Tenant,
    user: User,
    trip_id,
    passengers_payload: List[Dict],
    seat_selection: Dict,
    payment_payload: Dict,
):
    """
    Create booking + passengers + seats + compute price.
    Returns (booking, per_passenger_amount).
    """
    # Lock trip row for capacity-safe booking
    trip = (
        Trip.objects.select_for_update()
        .select_related("provider", "tenant", "route")
        .get(id=trip_id, tenant=tenant)
    )

    provider: Provider = trip.provider

    # Capacity check – count active seats
    active_bookings = Booking.objects.select_for_update().filter(
        trip=trip, status__in=["PENDING_PAYMENT", "CONFIRMED"]
    )
    existing_seats = (
        BookingPassenger.objects.filter(booking__in=active_bookings).count()
    )

    new_seats = len(passengers_payload)
    if trip.vehicle_capacity and existing_seats + new_seats > trip.vehicle_capacity:
        raise ValidationError("Not enough seats available for this trip.")

    # Compute per-passenger fare from route
    fare_info = calculate_fare_for_trip_from_route(trip)
    per_passenger_amount = fare_info["amount"]
    currency = fare_info["currency"]

    total_amount = per_passenger_amount * new_seats

    expires_at = timezone.now() + timedelta(minutes=15)

    booking = Booking.objects.create(
        tenant=tenant,
        provider=provider,
        trip=trip,
        customer_user=user,
        status="PENDING_PAYMENT",
        reservation_expires_at=expires_at,
        total_amount=total_amount,
        currency=currency,
        seats_count=new_seats,
        metadata={
            "pricing_components": fare_info.get("components", []),
            "distance_km": fare_info.get("distance_km"),
        },
    )

    passenger_objs = []
    for p in passengers_payload:
        passenger_objs.append(
            BookingPassenger.objects.create(
                booking=booking,
                passenger_type=p["type"],
                first_name=p["first_name"],
                last_name=p["last_name"],
                email=p.get("email", ""),
                phone=p.get("phone", ""),
            )
        )

    # simple seat allocation: map requested seats in order
    seat_req = (seat_selection or {}).get("requested_seats", [])
    if (seat_selection or {}).get("enabled") and seat_req:
        for idx, passenger in enumerate(passenger_objs):
            seat_num = seat_req[idx] if idx < len(seat_req) else ""
            BookingSeat.objects.create(
                booking=booking,
                passenger=passenger,
                seat_number=seat_num,
            )

    return booking, per_passenger_amount



@transaction.atomic
def confirm_booking_and_issue_tickets(booking: Booking):
    """
    Set booking to CONFIRMED and create tickets for all passengers.
    Idempotent: safe to call multiple times.
    """
    if booking.status == "CONFIRMED":
        # Already confirmed, ensure tickets exist
        if booking.tickets.exists():
            return booking
    elif booking.status != "PENDING_PAYMENT":
        raise ValidationError("Booking cannot be confirmed from its current status.")

    booking.status = "CONFIRMED"
    booking.save(update_fields=["status", "updated_at"])

    if not booking.tickets.exists():
        from apps.catalog.models import Trip

        trip: Trip = booking.trip
        valid_from = timezone.make_aware(
            timezone.datetime.combine(trip.service_date, trip.departure_time)
        )
        valid_until = timezone.make_aware(
            timezone.datetime.combine(trip.service_date, trip.arrival_time)
        )

        for passenger in booking.passengers.all():
            ticket_code = f"TKT-{booking.id.hex[:8]}-{uuid.uuid4().hex[:6]}".upper()
            qr_payload = f"{ticket_code}|booking={booking.id}|passenger={passenger.id}"
            Ticket.objects.create(
                tenant=booking.tenant,
                provider=booking.provider,
                booking=booking,
                passenger=passenger,
                ticket_code=ticket_code,
                qr_payload=qr_payload,
                valid_from=valid_from,
                valid_until=valid_until,
            )

    return booking


@transaction.atomic
def cancel_booking(booking: Booking, reason: str = "") -> Dict:
    """
    Cancel booking and (later) trigger refund logic.

    For now:
      - allow cancel if PENDING_PAYMENT or CONFIRMED
      - set status to CANCELLED
      - return simple refund info stub (you'll wire real policy later)
    """
    if booking.status not in ["PENDING_PAYMENT", "CONFIRMED"]:
        raise ValidationError("Booking cannot be cancelled in its current status.")

    previous_status = booking.status
    booking.status = "CANCELLED"
    booking.save(update_fields=["status", "updated_at"])

    # simple example: 100% refund if still pending payment, 0% if confirmed (you'll refine)
    refund_amount = 0
    if previous_status == "PENDING_PAYMENT":
        refund_amount = booking.total_amount

    return {
        "booking_id": str(booking.id),
        "previous_status": previous_status,
        "new_status": "CANCELLED",
        "refund": {
            "eligible": refund_amount > 0,
            "amount": refund_amount,
            "currency": booking.currency,
            "policy_code": "SIMPLE_POLICY",  # placeholder for later
        },
        "reason": reason,
    }



