from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from shifts.models import Shift
from notifications.models import Notification

@shared_task
def send_shift_reminders():
    now = timezone.now()
    reminder_time = now + timedelta(hours=1)
    shifts = Shift.objects.filter(start_time__range=(now, reminder_time), is_confirmed=True, status='scheduled')
    for shift in shifts:
        Notification.objects.create(
            user=shift.worker,
            message=f'Reminder: Your shift "{shift.name}" starts at {shift.start_time}.'
        )

@shared_task
def send_late_checkin_notifications():
    now = timezone.now()
    shifts = Shift.objects.filter(start_time__lt=now, status='scheduled', is_confirmed=True)
    for shift in shifts:
        attendance = shift.attendance_set.filter(check_in__isnull=False).first()
        if attendance and attendance.is_late:
            Notification.objects.create(
                user=shift.worker,
                message=f'Late check-in detected for your shift "{shift.name}" starting at {shift.start_time}.'
            )

@shared_task
def send_missed_shift_notifications():
    now = timezone.now()
    shifts = Shift.objects.filter(status='missed', is_confirmed=True)
    for shift in shifts:
        Notification.objects.create(
            user=shift.worker,
            message=f'You missed your shift "{shift.name}" scheduled at {shift.start_time}.'
        )

@shared_task
def send_checkout_reminders():
    now = timezone.now()
    attendances = Notification.objects.filter(check_out__isnull=True, check_in__isnull=False)
    for attendance in attendances:
        Notification.objects.create(
            user=attendance.user,
            message=f'Reminder: Please check out from your shift.'
        )
