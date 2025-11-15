from django.urls import path
from .views import AdminOverviewDashboardView, AdminSettlementSummaryView

urlpatterns = [
    path("dashboard/overview", AdminOverviewDashboardView.as_view(), name="admin-dashboard-overview"),
    path("reports/settlements", AdminSettlementSummaryView.as_view(), name="admin-reports-settlements"),
]
