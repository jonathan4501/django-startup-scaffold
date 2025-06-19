from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta, date
from django.contrib.auth import get_user_model
from django.db import models
from .models import MonthlyAttendanceSummary, AttendanceHeatmap
from attendance.models import Attendance

User = get_user_model()

@shared_task
def generate_monthly_attendance_summary():
    today = now().date()
    first_day_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_of_last_month = today.replace(day=1) - timedelta(days=1)

    users = User.objects.all()
    for user in users:
        # Calculate attendance summary for last month
        attendances = Attendance.objects.filter(
            user=user,
            check_in__date__gte=first_day_of_last_month,
            check_in__date__lte=last_day_of_last_month
        )
        total_days_worked = attendances.values('check_in__date').distinct().count()
        total_hours_worked = sum([(a.check_out - a.check_in).total_seconds() / 3600 for a in attendances if a.check_out and a.check_in])
        total_lateness_count = attendances.filter(is_late=True).count()
        total_work_days = (last_day_of_last_month - first_day_of_last_month).days + 1
        absence_ratio = 1 - (total_days_worked / total_work_days) if total_work_days > 0 else 0

        summary, created = MonthlyAttendanceSummary.objects.update_or_create(
            user=user,
            month=first_day_of_last_month,
            defaults={
                'total_days_worked': total_days_worked,
                'total_hours_worked': total_hours_worked,
                'total_lateness_count': total_lateness_count,
                'absence_ratio': absence_ratio,
            }
        )

@shared_task
def generate_attendance_heatmap():
    today = now().date()
    # Aggregate attendance data for today
    attendances = Attendance.objects.filter(check_in__date=today)
    total_attendances = attendances.count()
    punctuality_score = 0
    attendance_rate = 0

    if total_attendances > 0:
        punctuality_score = attendances.aggregate(avg_punctuality=models.Avg('punctuality_score'))['avg_punctuality'] or 0
        # Assuming total expected attendance is number of users
        total_users = User.objects.count()
        attendance_rate = total_attendances / total_users if total_users > 0 else 0

    heatmap, created = AttendanceHeatmap.objects.update_or_create(
        date=today,
        defaults={
            'punctuality_score': punctuality_score,
            'attendance_rate': attendance_rate,
        }
    )
