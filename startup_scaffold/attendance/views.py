from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Sum, F, ExpressionWrapper, DurationField, Count
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import Attendance, DailyAttendanceReport
from .serializers import AttendanceSerializer, DailyAttendanceReportSerializer
from .permissions import IsAdminOrSelf

User = get_user_model()

from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Sum, F, ExpressionWrapper, DurationField, Count
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import Attendance, DailyAttendanceReport
from .serializers import AttendanceSerializer, DailyAttendanceReportSerializer
from .permissions import IsAdminOrSelf
from rest_framework.decorators import action

User = get_user_model()

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        import math

        attendance = self.get_object()
        grace_period_minutes = 10  # Grace period in minutes, can be configurable
        now = timezone.now()
        shift_start = attendance.shift.start_time if attendance.shift else None

        # Geofencing validation
        shift = attendance.shift
        if shift and shift.geofence_lat is not None and shift.geofence_lng is not None and shift.geofence_radius_meters is not None:
            check_in_lat = request.data.get('check_in_lat')
            check_in_lng = request.data.get('check_in_lng')
            if check_in_lat is None or check_in_lng is None:
                return Response({'error': 'Check-in latitude and longitude are required for geofencing.'}, status=400)

            # Calculate distance between check-in location and geofence center
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371000  # Earth radius in meters
                phi1 = math.radians(float(lat1))
                phi2 = math.radians(float(lat2))
                delta_phi = math.radians(float(lat2) - float(lat1))
                delta_lambda = math.radians(float(lon2) - float(lon1))
                a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                return R * c

            distance = haversine(check_in_lat, check_in_lng, shift.geofence_lat, shift.geofence_lng)
            if distance > shift.geofence_radius_meters:
                # Log violation or deny check-in
                return Response({'error': 'Check-in location is outside the allowed geofence radius.'}, status=403)

        if shift_start:
            grace_period_end = shift_start + timedelta(minutes=grace_period_minutes)
            if now > grace_period_end:
                attendance.is_late = True
            else:
                attendance.is_late = False

        # Placeholder for biometric/face verification step
        biometric_verified = request.data.get('biometric_verified', False)
        if not biometric_verified:
            # In real implementation, integrate with biometric SDK or service
            # For now, just return a warning or allow to proceed based on config
            return Response({'warning': 'Biometric verification not completed. This is a placeholder.'}, status=200)

        attendance.check_in = now
        attendance.check_in_lat = request.data.get('check_in_lat')
        attendance.check_in_lng = request.data.get('check_in_lng')
        attendance.save()
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='check-out')
    def check_out(self, request, pk=None):
        attendance = self.get_object()
        attendance.check_out = timezone.now()
        attendance.save()
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)

class DailyAttendanceReportView(generics.ListAPIView):
    serializer_class = DailyAttendanceReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        month = self.request.query_params.get('month')
        if user.is_staff or user.is_superuser:
            qs = DailyAttendanceReport.objects.all()
        else:
            qs = DailyAttendanceReport.objects.filter(user=user)
        if month:
            try:
                month_date = datetime.strptime(month, '%Y-%m')
                start_date = month_date.replace(day=1)
                if month_date.month == 12:
                    end_date = month_date.replace(year=month_date.year+1, month=1, day=1)
                else:
                    end_date = month_date.replace(month=month_date.month+1, day=1)
                qs = qs.filter(date__gte=start_date, date__lt=end_date)
            except ValueError:
                qs = qs.none()
        return qs

class CurrentAttendanceStatusView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        # Users currently checked in (check_in <= now and (check_out is null or check_out > now))
        return Attendance.objects.filter(check_in__lte=now).filter(Q(check_out__isnull=True) | Q(check_out__gt=now))

class MyAttendanceHistoryView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Attendance.objects.filter(user=user).order_by('-check_in')[:30]

class AttendanceViolationsView(generics.ListAPIView):
    serializer_class = DailyAttendanceReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        week_start = timezone.now() - timedelta(days=7)
        if user.is_staff or user.is_superuser:
            qs = DailyAttendanceReport.objects.filter(date__gte=week_start).filter(Q(was_late=True) | Q(was_absent=True))
        else:
            qs = DailyAttendanceReport.objects.filter(user=user, date__gte=week_start).filter(Q(was_late=True) | Q(was_absent=True))
        return qs
