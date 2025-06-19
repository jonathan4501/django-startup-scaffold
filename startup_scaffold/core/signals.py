from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from attendance.models import Attendance
from core.models import AuditLog
import json

User = get_user_model()

@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, **kwargs):
    if created:
        # Place logic for user creation signal here
        print(f"User created: {instance}")

@receiver(pre_save, sender=Attendance)
def log_attendance_update(sender, instance, **kwargs):
    if not instance.pk:
        # New attendance record, no update
        return
    try:
        old_instance = Attendance.objects.get(pk=instance.pk)
    except Attendance.DoesNotExist:
        return

    changes = {}
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(instance, field_name)
        if old_value != new_value:
            changes[field_name] = {'old': old_value, 'new': new_value}

    if changes:
        AuditLog.objects.create(
            user=instance.user,
            action='update',
            model_name='Attendance',
            object_id=str(instance.pk),
            changes=json.dumps(changes),
        )
