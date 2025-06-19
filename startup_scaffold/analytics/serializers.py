from rest_framework import serializers
from .models import PlatformMetric, MonthlyAttendanceSummary, AttendanceHeatmap, AttendanceAnomaly

class PlatformMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformMetric
        fields = ['id', 'name', 'category', 'value', 'timestamp']

class MonthlyAttendanceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyAttendanceSummary
        fields = [
            'id',
            'user',
            'month',
            'total_days_worked',
            'total_hours_worked',
            'total_lateness_count',
            'absence_ratio',
        ]

class AttendanceHeatmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceHeatmap
        fields = [
            'id',
            'date',
            'punctuality_score',
            'attendance_rate',
        ]

class AttendanceAnomalySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceAnomaly
        fields = ['id', 'user', 'date_detected', 'description', 'resolved']

class DashboardMetricsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    avg_check_in_time = serializers.CharField()
    absent_today = serializers.IntegerField()
    late_today = serializers.IntegerField()

class TopPerformerSerializer(serializers.Serializer):
    user = serializers.CharField()
    metric_type = serializers.CharField()
    value = serializers.FloatField()
    month = serializers.DateField()
