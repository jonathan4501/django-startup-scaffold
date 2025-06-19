from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Shift
from django.core.mail import send_mail
from django.conf import settings
from attendance.models import Attendance, DailyAttendanceReport
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_shift_reminders():
    now = timezone.now()
    reminder_time = now + timedelta(hours=1)
    shifts = Shift.objects.filter(start_time__range=(now, reminder_time), is_confirmed=True, status='scheduled')
    for shift in shifts:
        # Send reminder email (example)
        send_mail(
            subject='Shift Reminder',
            message=f'Reminder: Your shift "{shift.name}" starts at {shift.start_time}.',
            from_email='no-reply@example.com',
            recipient_list=[shift.worker.email],
        )

@shared_task
def mark_missed_shifts():
    now = timezone.now()
    threshold_minutes = getattr(settings, 'SHIFT_MISSED_THRESHOLD_MINUTES', 0)
    threshold_time = now - timedelta(minutes=threshold_minutes)
    shifts = Shift.objects.filter(start_time__lt=threshold_time, status='scheduled', is_confirmed=True)
    for shift in shifts:
        shift.status = 'missed'
        shift.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Payment

@receiver(post_save, sender=Shift)
def create_payment_on_shift_completion(sender, instance, created, **kwargs):
    if not created and instance.status == 'completed':
        # Check if payment already exists for this shift
        if not Payment.objects.filter(shift=instance).exists():
            # Create a payment record linked to the shift and user
            Payment.objects.create(
                user=instance.worker,
                shift=instance,
                amount=calculate_payment_amount(instance),
                currency=get_local_currency(instance.worker),
                payment_method='shift_completion',
                payment_type='auto',
                status='initiated',
                transaction_id=generate_transaction_id(),
                initiated_at=timezone.now(),
            )

def calculate_payment_amount(shift):
    # Placeholder: calculate payment amount based on shift details
    # For example, fixed rate or based on job or duration
    # Here, just return a fixed amount for demonstration
    return 100.00

def get_local_currency(user):
    # Placeholder: determine user's local currency
    # Could be based on user profile or location
    return 'USD'

def generate_transaction_id():
    import uuid
    return str(uuid.uuid4())

@shared_task
def generate_daily_attendance_reports():
    today = timezone.now().date()
    users = User.objects.all()
    for user in users:
        attendances = Attendance.objects.filter(user=user, check_in__date=today)
        if attendances.exists():
            total_worked = attendances.aggregate(total=Sum('check_out') - Sum('check_in'))['total']
            was_late = any(att.check_in > att.shift.start_time for att in attendances if att.shift)
            late_minutes = 0
            for att in attendances:
                if att.shift and att.check_in > att.shift.start_time:
                    late_delta = att.check_in - att.shift.start_time
                    late_minutes += int(late_delta.total_seconds() // 60)
            checked_in = attendances.filter(check_in__isnull=False).exists()
            checked_out = attendances.filter(check_out__isnull=False).exists()
            DailyAttendanceReport.objects.update_or_create(
                user=user,
                date=today,
                defaults={
                    'total_worked_hours': total_worked or timedelta(0),
                    'was_late': was_late,
                    'late_minutes': late_minutes,
                    'was_absent': False,
                    'checked_in': checked_in,
                    'checked_out': checked_out,
                }
            )
        else:
            DailyAttendanceReport.objects.update_or_create(
                user=user,
                date=today,
                defaults={
                    'total_worked_hours': timedelta(0),
                    'was_late': False,
                    'late_minutes': 0,
                    'was_absent': True,
                    'checked_in': False,
                    'checked_out': False,
                }
            )

@shared_task
def mark_no_show_attendances():
    now = timezone.now()
    threshold_minutes = getattr(settings, 'SHIFT_MISSED_THRESHOLD_MINUTES', 0)
    threshold_time = now - timedelta(minutes=threshold_minutes)
    shifts = Shift.objects.filter(start_time__lt=threshold_time, status='scheduled', is_confirmed=True)
    for shift in shifts:
        attendance_exists = Attendance.objects.filter(shift=shift).exists()
        if not attendance_exists:
            shift.status = 'missed'
            shift.save()
