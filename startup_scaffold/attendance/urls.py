from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, DailyAttendanceReportView, CurrentAttendanceStatusView, MyAttendanceHistoryView, AttendanceViolationsView

router = DefaultRouter()
router.register(r'', AttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('report/', DailyAttendanceReportView.as_view(), name='daily-attendance-report'),
    path('status/now/', CurrentAttendanceStatusView.as_view(), name='current-attendance-status'),
    path('my-history/', MyAttendanceHistoryView.as_view(), name='my-attendance-history'),
    path('violations/', AttendanceViolationsView.as_view(), name='attendance-violations'),
]
