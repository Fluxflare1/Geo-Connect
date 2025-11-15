from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.providers.models import Provider
from .models import SupportTicket, SupportMessage
from .serializers import (
    SupportTicketCreateSerializer,
    SupportTicketListSerializer,
    SupportTicketDetailSerializer,
    SupportTicketUpdateSerializer,
    SupportMessageCreateSerializer,
)
from .permissions import IsTenantSupportOrAdmin

class CustomerSupportTicketListCreateView(generics.GenericAPIView):
    """
    GET/POST /api/v1/support/tickets (customer)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketCreateSerializer

    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        user = request.user
        qs = SupportTicket.objects.filter(tenant=tenant, customer_user=user).order_by(
            "-last_activity_at"
        )
        data = SupportTicketListSerializer(qs, many=True).data
        return Response({"tickets": data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        booking = None
        if data.get("booking_id"):
            try:
                booking = Booking.objects.get(id=data["booking_id"], tenant=tenant)
            except Booking.DoesNotExist:
                return Response(
                    {
                        "error": {
                            "code": "BOOKING_NOT_FOUND",
                            "message": "Booking not found for this tenant.",
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        provider = None
        if data.get("provider_id"):
            try:
                provider = Provider.objects.get(id=data["provider_id"], tenant=tenant)
            except Provider.DoesNotExist:
                return Response(
                    {
                        "error": {
                            "code": "PROVIDER_NOT_FOUND",
                            "message": "Provider not found for this tenant.",
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ticket = SupportTicket.objects.create(
            tenant=tenant,
            customer_user=user,
            provider=provider,
            booking=booking,
            subject=data["subject"],
            category=data["category"],
            priority=data["priority"],
        )

        SupportMessage.objects.create(
            ticket=ticket,
            sender=user,
            sender_type="CUSTOMER",
            body=data["message"],
            internal_only=False,
        )

        return Response(
            SupportTicketDetailSerializer(ticket).data, status=status.HTTP_201_CREATED
        )



class CustomerSupportTicketDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/support/tickets/{ticket_id}
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketDetailSerializer
    lookup_url_kwarg = "ticket_id"

    def get_queryset(self):
        return SupportTicket.objects.filter(
            tenant=self.request.tenant, customer_user=self.request.user
        )



class CustomerSupportMessageCreateView(generics.GenericAPIView):
    """
    POST /api/v1/support/tickets/{ticket_id}/messages
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SupportMessageCreateSerializer
    lookup_url_kwarg = "ticket_id"

    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        user = request.user
        try:
            ticket = SupportTicket.objects.get(
                id=kwargs[self.lookup_url_kwarg], tenant=tenant, customer_user=user
            )
        except SupportTicket.DoesNotExist:
            return Response(
                {"error": {"code": "TICKET_NOT_FOUND", "message": "Ticket not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        msg = SupportMessage.objects.create(
            ticket=ticket,
            sender=user,
            sender_type="CUSTOMER",
            body=data["body"],
            internal_only=False,
        )
        ticket.last_activity_at = timezone.now()
        ticket.save(update_fields=["last_activity_at"])

        return Response(
            SupportMessageSerializer(msg).data, status=status.HTTP_201_CREATED
        )


class AdminSupportTicketListView(generics.ListAPIView):
    """
    GET /api/v1/admin/support/tickets
    """
    permission_classes = [IsAuthenticated, IsTenantSupportOrAdmin]
    serializer_class = SupportTicketListSerializer

    def get_queryset(self):
        tenant = self.request.tenant
        qs = SupportTicket.objects.filter(tenant=tenant)

        status_filter = self.request.query_params.get("status")
        priority_filter = self.request.query_params.get("priority")
        category_filter = self.request.query_params.get("category")

        if status_filter:
            qs = qs.filter(status=status_filter)
        if priority_filter:
            qs = qs.filter(priority=priority_filter)
        if category_filter:
            qs = qs.filter(category=category_filter)

        return qs.order_by("-last_activity_at")



class AdminSupportTicketDetailView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/v1/admin/support/tickets/{ticket_id}
    """
    permission_classes = [IsAuthenticated, IsTenantSupportOrAdmin]
    serializer_class = SupportTicketUpdateSerializer
    lookup_url_kwarg = "ticket_id"

    def get_queryset(self):
        return SupportTicket.objects.filter(tenant=self.request.tenant)

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        data = SupportTicketDetailSerializer(ticket).data
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        ticket = self.get_object()
        serializer = self.get_serializer(ticket, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SupportTicketDetailSerializer(ticket).data, status=status.HTTP_200_OK)



class AdminSupportMessageCreateView(generics.GenericAPIView):
    """
    POST /api/v1/admin/support/tickets/{ticket_id}/messages
    """
    permission_classes = [IsAuthenticated, IsTenantSupportOrAdmin]
    serializer_class = SupportMessageCreateSerializer
    lookup_url_kwarg = "ticket_id"

    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        user = request.user
        try:
            ticket = SupportTicket.objects.get(
                id=kwargs[self.lookup_url_kwarg], tenant=tenant
            )
        except SupportTicket.DoesNotExist:
            return Response(
                {"error": {"code": "TICKET_NOT_FOUND", "message": "Ticket not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        msg = SupportMessage.objects.create(
            ticket=ticket,
            sender=user,
            sender_type="AGENT",
            body=data["body"],
            internal_only=data.get("internal_only", False),
        )
        ticket.last_activity_at = timezone.now()
        ticket.save(update_fields=["last_activity_at"])

        return Response(
            SupportMessageSerializer(msg).data, status=status.HTTP_201_CREATED
        )
