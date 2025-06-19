import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from services.models import Skill

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.country}"

class Job(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)  # For backward compatibility with tests
    description = models.TextField(blank=True, null=True)
    required_skills = models.ManyToManyField(Skill, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shift = models.ForeignKey('shifts.Shift', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_job')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    max_workers = models.PositiveIntegerField(default=1)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        if self.budget is not None and self.budget <= 0:
            raise ValidationError("Budget must be greater than 0.")

    @property
    def is_expired(self):
        return self.expiry_date and timezone.now() > self.expiry_date

class JobApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    is_hired = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.worker.email} application for {self.job.title}"

    def clean(self):
        # Limit one active application per worker per job
        if JobApplication.objects.filter(job=self.job, worker=self.worker).exclude(id=self.id).exists():
            raise ValidationError("Worker has already applied to this job.")

class JobRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_recommendations')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommended_to')
    recommended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation of {self.job.title} to {self.worker.email}"

# Signal to trigger rating creation when job is completed
from django.db.models.signals import post_save
from django.dispatch import receiver
from ratings.models import Review

@receiver(post_save, sender=Job)
def create_ratings_on_job_completion(sender, instance, **kwargs):
    if instance.status == Job.Status.COMPLETED:
        # Create rating placeholders for client and hired workers
        hired_applications = instance.applications.filter(is_hired=True)
        for application in hired_applications:
            # Create rating from client to worker
            Review.objects.get_or_create(
                rater=instance.client,
                ratee=application.worker,
                job=instance,
                defaults={'rating': None, 'comment': ''}
            )
            # Create rating from worker to client
            Review.objects.get_or_create(
                rater=application.worker,
                ratee=instance.client,
                job=instance,
                defaults={'rating': None, 'comment': ''}
            )
