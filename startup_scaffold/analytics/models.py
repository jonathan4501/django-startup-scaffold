from django.db import models
from django.conf import settings
from datetime import date

class PlatformMetric(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)  # New field for metric category/tag
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} at {self.timestamp}: {self.value}"

class MonthlyAttendanceSummary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    month = models.DateField()  # store first day of month
    total_days_worked = models.IntegerField(default=0)
    total_hours_worked = models.FloatField(default=0.0)  # store hours as float
    total_lateness_count = models.IntegerField(default=0)
    absence_ratio = models.FloatField(default=0.0)  # ratio of absent days to total work days

    class Meta:
        unique_together = ('user', 'month')

    def __str__(self):
        return f"Monthly Summary for {self.user} - {self.month.strftime('%Y-%m')}"

class AttendanceHeatmap(models.Model):
    date = models.DateField()
    punctuality_score = models.FloatField()  # e.g., average punctuality score for org/team
    attendance_rate = models.FloatField()  # e.g., % attendance for org/team

    def __str__(self):
        return f"Heatmap for {self.date}"

class AttendanceAnomaly(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    date_detected = models.DateField(auto_now_add=True)
    description = models.TextField()
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Anomaly for {self.user} detected on {self.date_detected}"
