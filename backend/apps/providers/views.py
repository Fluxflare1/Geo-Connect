from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Provider
from .serializers import ProviderPublicProfileSerializer
from .permissions import IsProviderUserOrTenantAdmin


class ProviderProfileView(generics.RetrieveAPIView):
    """
    GET /api/v1/provider/profile

    Returns the provider profile associated with X-Provider-ID and tenant.
    """
    permission_classes = [IsAuthenticated, IsProviderUserOrTenantAdmin]
    serializer_class = ProviderPublicProfileSerializer

    def get_object(self):
        # permission class has already set request.provider
        return self.request.provider
