from django.contrib import admin
from .models import PlatformMetric, MonthlyAttendanceSummary, AttendanceHeatmap

@admin.register(PlatformMetric)
class PlatformMetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'timestamp')
    list_filter = ('name', 'timestamp')
    search_fields = ('name',)

@admin.register(MonthlyAttendanceSummary)
class MonthlyAttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'total_days_worked', 'total_hours_worked', 'total_lateness_count', 'absence_ratio')
    list_filter = ('month', 'user')
    search_fields = ('user__username',)

@admin.register(AttendanceHeatmap)
class AttendanceHeatmapAdmin(admin.ModelAdmin):
    list_display = ('date', 'punctuality_score', 'attendance_rate')
    list_filter = ('date',)
