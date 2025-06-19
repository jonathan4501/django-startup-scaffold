from rest_framework import viewsets, permissions, generics, views, response, status
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from datetime import datetime, timedelta
from .models import PlatformMetric, MonthlyAttendanceSummary, AttendanceHeatmap
from .serializers import PlatformMetricSerializer, MonthlyAttendanceSummarySerializer, AttendanceHeatmapSerializer
from attendance.models import Attendance
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import viewsets, permissions, generics, views, response, status
from django.db.models import Avg, F, ExpressionWrapper, DurationField, Q, Count
from datetime import datetime, timedelta
from .models import PlatformMetric, MonthlyAttendanceSummary, AttendanceHeatmap, AttendanceAnomaly
from .serializers import (
    PlatformMetricSerializer,
    MonthlyAttendanceSummarySerializer,
    AttendanceHeatmapSerializer,
    AttendanceAnomalySerializer,
    DashboardMetricsSerializer,
    TopPerformerSerializer,
)
from attendance.models import Attendance
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
import csv

User = get_user_model()

class PlatformMetricViewSet(viewsets.ModelViewSet):
    queryset = PlatformMetric.objects.all()
    serializer_class = PlatformMetricSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return PlatformMetric.objects.all()
        # For regular users, filter by category or other logic if needed
        return PlatformMetric.objects.filter(category__isnull=False)  # Example filter

class MonthlyAttendanceSummaryView(generics.ListAPIView):
    serializer_class = MonthlyAttendanceSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get('user_id')
        if user.is_staff or user.is_superuser:
            if user_id:
                return MonthlyAttendanceSummary.objects.filter(user_id=user_id).order_by('-month')
            return MonthlyAttendanceSummary.objects.all().order_by('-month')
        else:
            # Regular users can only see their own summaries
            return MonthlyAttendanceSummary.objects.filter(user=user).order_by('-month')

class AttendanceHeatmapView(generics.ListAPIView):
    serializer_class = AttendanceHeatmapSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return AttendanceHeatmap.objects.all().order_by('-date')
        # For regular users, filter by date or other logic if needed
        return AttendanceHeatmap.objects.all().order_by('-date')  # Adjust as needed

class AverageCheckInTimeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_id = request.query_params.get('user_id')
        queryset = Attendance.objects.filter(check_in__isnull=False)

        if not (user.is_staff or user.is_superuser):
            queryset = queryset.filter(user=user)
        elif user_id:
            queryset = queryset.filter(user_id=user_id)

        avg_seconds = queryset.annotate(
            check_in_seconds=ExpressionWrapper(
                F('check_in__hour') * 3600 + F('check_in__minute') * 60 + F('check_in__second'),
                output_field=DurationField()
            )
        ).aggregate(avg_seconds=Avg('check_in_seconds'))['avg_seconds']

        if avg_seconds is None:
            return response.Response({'average_check_in_time': None}, status=status.HTTP_200_OK)

        avg_time = (datetime.min + timedelta(seconds=avg_seconds)).time()
        return response.Response({'average_check_in_time': avg_time.strftime('%H:%M:%S')}, status=status.HTTP_200_OK)

class DashboardMetricsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        total_users = User.objects.count()
        today = datetime.today().date()
        active_users_today = Attendance.objects.filter(check_in__date=today).values('user').distinct().count()
        avg_check_in_time = Attendance.objects.filter(check_in__date=today).annotate(
            check_in_seconds=ExpressionWrapper(
                F('check_in__hour') * 3600 + F('check_in__minute') * 60 + F('check_in__second'),
                output_field=DurationField()
            )
        ).aggregate(avg_seconds=Avg('check_in_seconds'))['avg_seconds']
        if avg_check_in_time is not None:
            avg_check_in_time = (datetime.min + timedelta(seconds=avg_check_in_time)).time().strftime('%H:%M:%S')
        else:
            avg_check_in_time = None

        absent_today = total_users - active_users_today
        late_today = Attendance.objects.filter(check_in__date=today, is_late=True).count()

        data = {
            'total_users': total_users,
            'active_users_today': active_users_today,
            'avg_check_in_time': avg_check_in_time,
            'absent_today': absent_today,
            'late_today': late_today,
        }
        serializer = DashboardMetricsSerializer(data)
        return Response(serializer.data)

class TopPerformersView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        metric_type = request.query_params.get('metric_type', 'total_hours_worked')
        month = request.query_params.get('month')
        queryset = MonthlyAttendanceSummary.objects.all()

        if month:
            queryset = queryset.filter(month=month)

        if metric_type not in ['total_hours_worked', 'total_lateness_count', 'absence_ratio']:
            return Response({'detail': 'Invalid metric_type'}, status=status.HTTP_400_BAD_REQUEST)

        if metric_type == 'absence_ratio':
            queryset = queryset.order_by(metric_type)
        else:
            queryset = queryset.order_by('-' + metric_type)

        top_users = queryset[:10]
        results = []
        for item in top_users:
            results.append({
                'user': item.user.username,
                'metric_type': metric_type,
                'value': getattr(item, metric_type),
                'month': item.month,
            })

        serializer = TopPerformerSerializer(results, many=True)
        return Response(serializer.data)

class ExportMonthlySummaryCSVView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="monthly_attendance_summary.csv"'

        writer = csv.writer(response)
        writer.writerow(['User', 'Month', 'Total Days Worked', 'Total Hours Worked', 'Total Lateness Count', 'Absence Ratio'])

        summaries = MonthlyAttendanceSummary.objects.all()
        for summary in summaries:
            writer.writerow([
                summary.user.username,
                summary.month.strftime('%Y-%m'),
                summary.total_days_worked,
                summary.total_hours_worked,
                summary.total_lateness_count,
                summary.absence_ratio,
            ])

        return response

class ExportAttendanceHeatmapCSVView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_heatmap.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Punctuality Score', 'Attendance Rate'])

        heatmaps = AttendanceHeatmap.objects.all()
        for heatmap in heatmaps:
            writer.writerow([
                heatmap.date.strftime('%Y-%m-%d'),
                heatmap.punctuality_score,
                heatmap.attendance_rate,
            ])

        return response

class AnomalyDetectionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        anomalies = AttendanceAnomaly.objects.filter(resolved=False)
        serializer = AttendanceAnomalySerializer(anomalies, many=True)
        return Response(serializer.data)
