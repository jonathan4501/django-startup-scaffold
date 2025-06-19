from rest_framework import serializers
from .models import Attendance, DailyAttendanceReport

class AttendanceSerializer(serializers.ModelSerializer):
    total_hours = serializers.DurationField(read_only=True)

    class Meta:
        model = Attendance
        fields = ('id', 'user', 'shift', 'check_in', 'check_out', 'check_in_lat', 'check_in_lng', 'check_out_lat', 'check_out_lng', 'device_type', 'total_hours', 'created_at', 'updated_at')

class DailyAttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAttendanceReport
        fields = '__all__'
