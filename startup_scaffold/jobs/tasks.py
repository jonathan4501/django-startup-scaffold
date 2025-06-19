from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Job, JobRecommendation

User = get_user_model()

@shared_task
def recommend_jobs_for_all_users():
    users = User.objects.all()
    for user in users:
        recommend_jobs_for_user(user)

def recommend_jobs_for_user(user):
    # Clear existing recommendations
    JobRecommendation.objects.filter(worker=user).delete()

    # Get jobs matching user's skills and location
    if hasattr(user, 'profile') and user.profile.location:
        # Example of weighted recommendation: 70% skills, 30% location
        skill_jobs = Job.objects.filter(
            required_skills__in=user.skills.all(),
            status=Job.Status.OPEN
        )
        location_jobs = Job.objects.filter(
            location=user.profile.location,
            status=Job.Status.OPEN
        )
        # Combine and rank jobs (simple union here, can be improved)
        matching_jobs = (skill_jobs | location_jobs).distinct().exclude(applications__worker=user)

        # Create new recommendations
        for job in matching_jobs:
            JobRecommendation.objects.create(worker=user, job=job)

@shared_task
def mark_expired_jobs():
    now = timezone.now()
    expired_jobs = Job.objects.filter(expiry_date__lt=now, status=Job.Status.OPEN)
    for job in expired_jobs:
        job.status = Job.Status.CANCELLED
        job.save()
