from django.conf import settings
from django.db import models
from core.models import TimeStampedModel, UUIDModel
from jobs.models import Job

class Shift(UUIDModel, TimeStampedModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='shifts')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shifts')
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('missed', 'Missed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')
    notes = models.TextField(blank=True)
    worker_feedback = models.TextField(blank=True)

    # Geofencing fields
    geofence_lat = models.FloatField(null=True, blank=True)
    geofence_lng = models.FloatField(null=True, blank=True)
    geofence_radius_meters = models.FloatField(null=True, blank=True)  # allowed radius in meters

    def __str__(self):
        return f"{self.name} | {self.worker.email} | {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    @property
    def duration(self):
        return self.end_time - self.start_time


