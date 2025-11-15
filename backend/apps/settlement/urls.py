from django.urls import path
from .views import SettlementBatchListCreateView, SettlementBatchDetailView

urlpatterns = [
    path("settlements/batches", SettlementBatchListCreateView.as_view(), name="settlements-batches-list-create"),
    path("settlements/batches/<uuid:batch_id>", SettlementBatchDetailView.as_view(), name="settlements-batches-detail"),
]
