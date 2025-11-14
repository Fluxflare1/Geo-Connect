from django.urls import path
from .views import WebhookEndpointListCreateView, WebhookEndpointDetailView

urlpatterns = [
    path(
        "notifications/webhooks",
        WebhookEndpointListCreateView.as_view(),
        name="admin-webhooks-list-create",
    ),
    path(
        "notifications/webhooks/<uuid:endpoint_id>",
        WebhookEndpointDetailView.as_view(),
        name="admin-webhooks-detail",
    ),
]
