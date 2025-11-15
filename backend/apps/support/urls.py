from django.urls import path

from .views import (
    CustomerSupportTicketListCreateView,
    CustomerSupportTicketDetailView,
    CustomerSupportMessageCreateView,
    AdminSupportTicketListView,
    AdminSupportTicketDetailView,
    AdminSupportMessageCreateView,
)

urlpatterns = [
    # Customer endpoints
    path("support/tickets", CustomerSupportTicketListCreateView.as_view(), name="support-tickets-customer"),
    path("support/tickets/<uuid:ticket_id>", CustomerSupportTicketDetailView.as_view(), name="support-ticket-detail-customer"),
    path("support/tickets/<uuid:ticket_id>/messages", CustomerSupportMessageCreateView.as_view(), name="support-ticket-messages-customer"),

    # Admin/support endpoints (under /api/v1/admin/... via separate include)
    path("support/tickets", AdminSupportTicketListView.as_view(), name="support-tickets-admin"),
    path("support/tickets/<uuid:ticket_id>", AdminSupportTicketDetailView.as_view(), name="support-ticket-detail-admin"),
    path("support/tickets/<uuid:ticket_id>/messages", AdminSupportMessageCreateView.as_view(), name="support-ticket-messages-admin"),
]
