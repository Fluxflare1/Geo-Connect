from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Booking
from .serializers import (
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingCancelSerializer,
)
from .services import create_booking, cancel_booking
from apps.payments.services import create_payment_for_booking
from apps.iam.permissions import IsTenantAdmin
from apps.core.services import register_idempotency_key, IdempotencyError



class BookingCreateView(generics.GenericAPIView):
    """
    POST /api/v1/bookings

    Requires authenticated user in a tenant context.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCreateSerializer

    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        if tenant is None:
            return Response(
                {"error": {"code": "TENANT_REQUIRED", "message": "Tenant context required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            booking, per_passenger_amount = create_booking(
                tenant=tenant,
                user=request.user,
                trip_id=data["trip_id"],
                passengers_payload=data["passengers"],
                seat_selection=data.get("seat_selection") or {},
                payment_payload=data["payment"],
            )
        except ValidationError as e:
            return Response(
                {
                    "error": {
                        "code": "BOOKING_ERROR",
                        "message": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_session = create_payment_for_booking(
            request=request,
            booking=booking,
            provider_code=data["payment"]["provider"],
        )

        booking_data = BookingDetailSerializer(booking).data
        return Response(
            {
                "booking": booking_data,
                "payment_session": payment_session,
            },
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/bookings/{booking_id}
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingDetailSerializer
    lookup_url_kwarg = "booking_id"

    def get_queryset(self):
        tenant = self.request.tenant
        user = self.request.user
        qs = Booking.objects.select_related("tenant", "provider", "trip").prefetch_related(
            "passengers", "tickets"
        )
        if user.role == "PLATFORM_SUPER_ADMIN":
            return qs
        if tenant:
            qs = qs.filter(tenant=tenant)
        if user.role == "PASSENGER":
            qs = qs.filter(customer_user=user)
        return qs


class BookingCancelView(generics.GenericAPIView):
    """
    POST /api/v1/bookings/{booking_id}/cancel
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCancelSerializer
    lookup_url_kwarg = "booking_id"

    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        user = request.user
        try:
            booking = Booking.objects.select_related("tenant").get(
                id=kwargs[self.lookup_url_kwarg], tenant=tenant
            )
        except Booking.DoesNotExist:
            return Response(
                {
                    "error": {
                        "code": "BOOKING_NOT_FOUND",
                        "message": "Booking not found.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # basic access rule: owner or tenant admin
        if user.role not in ["TENANT_OWNER", "TENANT_ADMIN", "PLATFORM_SUPER_ADMIN"]:
            if booking.customer_user_id != user.id:
                return Response(
                    {
                        "error": {
                            "code": "FORBIDDEN",
                            "message": "You cannot cancel this booking.",
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get("reason", "")

        try:
            result = cancel_booking(booking, reason=reason)
        except ValidationError as e:
            return Response(
                {
                    "error": {
                        "code": "BOOKING_INVALID_STATE",
                        "message": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_200_OK)
