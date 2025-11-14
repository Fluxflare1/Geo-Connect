from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.iam.permissions import IsTenantAdmin
from .models import WebhookEndpoint
from .serializers import WebhookEndpointSerializer


class WebhookEndpointListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = WebhookEndpointSerializer

    def get_queryset(self):
        return WebhookEndpoint.objects.filter(tenant=self.request.tenant).order_by("name")

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class WebhookEndpointDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = WebhookEndpointSerializer
    lookup_url_kwarg = "endpoint_id"

    def get_queryset(self):
        return WebhookEndpoint.objects.filter(tenant=self.request.tenant)
