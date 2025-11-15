from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.iam.permissions import IsTenantAdmin
from .models import SettlementBatch
from .serializers import (
    SettlementBatchSerializer,
    SettlementBatchCreateSerializer,
)
from .services import generate_settlement_batch

class SettlementBatchListCreateView(generics.GenericAPIView):
    """
    GET/POST /api/v1/admin/settlements/batches
    """
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = SettlementBatchCreateSerializer

    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        qs = SettlementBatch.objects.filter(tenant=tenant).order_by("-created_at")
        data = SettlementBatchSerializer(qs, many=True).data
        return Response({"batches": data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        tenant = request.tenant
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        batch = generate_settlement_batch(
            tenant=tenant,
            from_date=data["from_date"],
            to_date=data["to_date"],
        )
        if data.get("notes"):
            batch.notes = data["notes"]
            batch.save(update_fields=["notes"])

        return Response(SettlementBatchSerializer(batch).data, status=status.HTTP_201_CREATED)


class SettlementBatchDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/admin/settlements/batches/{batch_id}
    """
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = SettlementBatchSerializer
    lookup_url_kwarg = "batch_id"

    def get_queryset(self):
        return SettlementBatch.objects.filter(tenant=self.request.tenant)

  
