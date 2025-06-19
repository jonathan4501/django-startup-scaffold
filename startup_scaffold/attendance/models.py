import uuid
from django.db import models
from django.conf import settings
from shifts.models import Shift
from datetime import timedelta

class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    check_in_lat = models.FloatField(null=True, blank=True)
    check_in_lng = models.FloatField(null=True, blank=True)
    check_out_lat = models.FloatField(null=True, blank=True)
    check_out_lng = models.FloatField(null=True, blank=True)
    device_type = models.CharField(max_length=20, default="web")  # or 'mobile'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_hours(self):
        if self.check_in and self.check_out:
            return self.check_out - self.check_in
        return timedelta(0)

    def __str__(self):
        return f"{self.user} - {self.check_in.date()}"

class DailyAttendanceReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    total_worked_hours = models.DurationField()
    late_minutes = models.IntegerField(default=0)
    was_late = models.BooleanField(default=False)
    was_absent = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"Report for {self.user} on {self.date}"
