from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlatformMetricViewSet,
    MonthlyAttendanceSummaryView,
    AttendanceHeatmapView,
    AverageCheckInTimeView,
    DashboardMetricsView,
    TopPerformersView,
    ExportMonthlySummaryCSVView,
    ExportAttendanceHeatmapCSVView,
    AnomalyDetectionView,
)

router = DefaultRouter()
router.register(r'platform-metrics', PlatformMetricViewSet, basename='platformmetric')

urlpatterns = [
    path('', include(router.urls)),
    path('monthly-summary/', MonthlyAttendanceSummaryView.as_view(), name='monthly-attendance-summary'),
    path('heatmap/', AttendanceHeatmapView.as_view(), name='attendance-heatmap'),
    path('average-checkin-time/', AverageCheckInTimeView.as_view(), name='average-checkin-time'),
    path('dashboard-metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('top-performers/', TopPerformersView.as_view(), name='top-performers'),
    path('export/monthly-summary/', ExportMonthlySummaryCSVView.as_view(), name='export-monthly-summary'),
    path('export/attendance-heatmap/', ExportAttendanceHeatmapCSVView.as_view(), name='export-attendance-heatmap'),
    path('anomalies/', AnomalyDetectionView.as_view(), name='anomaly-detection'),
]
