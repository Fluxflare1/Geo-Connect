from django.urls import path
from .views import PaymentWebhookView

urlpatterns = [
    path(
        "payments/webhooks/<str:provider>",
        PaymentWebhookView.as_view(),
        name="payments-webhook",
    ),
]
